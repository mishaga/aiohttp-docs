import inspect
from collections.abc import Generator
from http import HTTPMethod, HTTPStatus

from aiohttp import web
from aiohttp.typedefs import Handler
from aiohttp.web_urldispatcher import AbstractRoute
from pydantic import BaseModel

from ._constants import DOCS_ATTR_NAME, OPENAPI_SPEC_VERSION
from ._doc_models import ApiEndpoint, Response, Responses
from ._enums import ParameterType
from ._inner_models import RouteInfo
from ._spec_models import Components, Info, OpenApiSpecification, Operation, Parameter, PathItem, Server


def rewrite_defs_refs[T](obj: T) -> T:
    """Recursively rewrite $ref paths from #/$defs/ to #/components/schemas/."""
    if isinstance(obj, dict):
        return {
            k: v.replace('#/$defs/', '#/components/schemas/')
            if k == '$ref' and isinstance(v, str)
            else rewrite_defs_refs(v)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [rewrite_defs_refs(item) for item in obj]

    return obj


class SchemaCollector:
    """Collects Pydantic model schemas for the OpenAPI components/schemas section."""

    def __init__(self) -> None:
        self.schemas: dict[str, dict] = {}

    def add_schema_model(self, model_class: type[BaseModel]) -> dict:
        """Add a model to components/schemas and return a $ref dict."""
        name = model_class.__name__
        if name not in self.schemas:
            schema = model_class.model_json_schema()
            self._extract_defs(schema)
            self.schemas[name] = rewrite_defs_refs(schema)
        return {'$ref': f'#/components/schemas/{name}'}

    def process_parameter(self, model_class: type[BaseModel]) -> dict:
        """Process a model schema for field extraction: extract $defs and rewrite refs.

        Used for parameter models where individual field schemas are needed,
        but the model itself should not appear in components/schemas.
        """
        schema = model_class.model_json_schema()
        self._extract_defs(schema)
        return rewrite_defs_refs(schema)

    def _extract_defs(self, schema: dict) -> None:
        """Extract $defs from a schema and add them to collected schemas."""
        defs = schema.pop('$defs', {})
        for def_name, def_schema in defs.items():
            if def_name not in self.schemas:
                self.schemas[def_name] = rewrite_defs_refs(def_schema)


def build_openapi_spec(
    app: web.Application,
    *,
    info: Info,
    servers: list[Server] | None = None,
) -> OpenApiSpecification:
    """Build OpenAPI 3.1 specification from application routes."""
    paths: dict[str, PathItem] = {}
    collector = SchemaCollector()

    for route in app.router.routes():
        for route_info in extract_route_info(route, collector):
            if route_info.path not in paths:
                paths[route_info.path] = PathItem()
            paths[route_info.path][route_info.method.lower()] = route_info.operation

    spec = OpenApiSpecification(
        openapi=OPENAPI_SPEC_VERSION,
        info=info,
        paths=paths,
    )

    if servers:
        spec['servers'] = servers

    if collector.schemas:
        spec['components'] = Components(
            schemas=collector.schemas,
        )

    return spec


def extract_route_info(
    route: AbstractRoute,
    collector: SchemaCollector,
) -> Generator[RouteInfo]:
    if inspect.isfunction(route.handler) and hasattr(route.handler, DOCS_ATTR_NAME):
        method = HTTPMethod(route.method)
        path = route.resource.canonical
        operation = extract_operation(route.handler, collector)
        yield RouteInfo(
            method=method,
            path=path,
            operation=operation,
        )

    elif inspect.isclass(route.handler):
        for m in HTTPMethod:
            method = HTTPMethod(m)
            handler = getattr(route.handler, method.lower(), None)
            if handler and hasattr(handler, DOCS_ATTR_NAME):
                path = route.resource.canonical
                operation = extract_operation(handler, collector)
                yield RouteInfo(
                    method=method,
                    path=path,
                    operation=operation,
                )


def extract_operation(
    handler: Handler,
    collector: SchemaCollector,
) -> Operation:
    """Extract OpenAPI path information from a documented route."""
    docs_data: ApiEndpoint = getattr(handler, DOCS_ATTR_NAME)
    parameters = get_parameters(docs_data=docs_data, collector=collector)

    operation: Operation = {}

    if 'tags' in docs_data:
        operation['tags'] = docs_data['tags']

    if 'summary' in docs_data:
        operation['summary'] = docs_data['summary']

    if 'description' in docs_data:
        operation['description'] = docs_data['description']
    else:
        docstring = inspect.getdoc(handler)
        if docstring:
            operation['description'] = docstring

    if 'deprecated' in docs_data:
        operation['deprecated'] = docs_data['deprecated']
    elif hasattr(handler, '__deprecated__'):
        operation['deprecated'] = True

    if parameters:
        operation['parameters'] = parameters

    if 'body_model' in docs_data:
        operation['requestBody'] = get_request_body(
            model_class=docs_data['body_model'],
            required=True,
            collector=collector,
        )

    if docs_data['response_models']:
        operation['responses'] = get_responses(docs_data['response_models'], collector)

    return operation


def get_responses(
    response_models: Responses,
    collector: SchemaCollector,
) -> dict[str, dict]:
    responses = {}

    for status_code, data in response_models.items():
        if not isinstance(status_code, HTTPStatus):
            status_code = HTTPStatus(status_code)  # noqa: PLW2901

        response = data
        if inspect.isclass(data) and issubclass(data, BaseModel):
            response = Response(model=data)

        response_object: dict = {
            'description': response.get('description', status_code.phrase),
        }

        if 'model' in response:
            response_object['content'] = {
                'application/json': {
                    'schema': collector.add_schema_model(response['model']),
                },
            }

        responses[status_code.value] = response_object

    return responses


def get_request_body(
    model_class: type[BaseModel],
    *,
    required: bool,
    collector: SchemaCollector,
) -> dict:
    return {
        'required': required,
        'content': {
            'application/json': {
                'schema': collector.add_schema_model(model_class),
            },
        },
    }


def get_parameter_by_type(
    model_class: type[BaseModel],
    parameter_type: ParameterType,
    collector: SchemaCollector,
) -> list[Parameter]:
    schema = collector.process_parameter(model_class)
    properties = []

    for field_name, field_info in model_class.model_fields.items():
        schema_prop_name = field_info.alias or field_name
        field_schema = schema['properties'][schema_prop_name]
        field_schema.pop('description', None)
        field_schema.pop('examples', None)

        parameter: Parameter = {
            'name': field_info.serialization_alias or field_name,
            'in': parameter_type,
            'required': field_info.is_required(),
            'deprecated': bool(field_info.deprecated),
            'schema': field_schema,
        }

        if field_info.description:
            parameter['description'] = field_info.description

        if field_info.examples:
            examples = {}
            for example in field_info.examples:
                key = example.get('summary') or example.get('value') or example.get('description', '')
                examples[key] = example
            parameter['examples'] = examples

        properties.append(parameter)

    return properties


def get_parameters(docs_data: ApiEndpoint, *, collector: SchemaCollector) -> list[Parameter]:
    parameters = []

    if 'path_model' in docs_data:
        parameters.extend(
            get_parameter_by_type(
                model_class=docs_data['path_model'],
                parameter_type=ParameterType.PATH,
                collector=collector,
            ),
        )

    if 'query_model' in docs_data:
        parameters.extend(
            get_parameter_by_type(
                model_class=docs_data['query_model'],
                parameter_type=ParameterType.QUERY,
                collector=collector,
            ),
        )

    if 'header_model' in docs_data:
        parameters.extend(
            get_parameter_by_type(
                model_class=docs_data['header_model'],
                parameter_type=ParameterType.HEADER,
                collector=collector,
            ),
        )

    if 'cookie_model' in docs_data:
        parameters.extend(
            get_parameter_by_type(
                model_class=docs_data['cookie_model'],
                parameter_type=ParameterType.COOKIE,
                collector=collector,
            ),
        )

    return parameters
