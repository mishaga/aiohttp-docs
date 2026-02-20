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
from ._spec_models import Info, OpenApiSpecification, Operation, Parameter, PathItem


def build_openapi_spec(
    app: web.Application,
    *,
    info: Info,
) -> OpenApiSpecification:
    """Build OpenAPI 3.1 specification from application routes."""
    paths: dict[str, PathItem] = {}

    for route in app.router.routes():
        for handler in extract_route_info(route):
            if handler.path not in paths:
                paths[handler.path] = PathItem()
            paths[handler.path][handler.method.lower()] = handler.operation

    return OpenApiSpecification(
        openapi=OPENAPI_SPEC_VERSION,
        info=info,
        paths=paths,
    )


def extract_route_info(route: AbstractRoute) -> Generator[RouteInfo]:
    if inspect.isfunction(route.handler) and hasattr(route.handler, DOCS_ATTR_NAME):
        method = HTTPMethod(route.method)
        path = route.resource.canonical
        operation = extract_operation(route.handler)
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
                operation = extract_operation(handler)
                yield RouteInfo(
                    method=method,
                    path=path,
                    operation=operation,
                )


def extract_operation(handler: Handler) -> Operation:
    """Extract OpenAPI path information from a documented route."""
    docs_data: ApiEndpoint = getattr(handler, DOCS_ATTR_NAME)
    parameters = get_parameters(docs_data=docs_data)

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
        )

    if docs_data.get('response_models'):
        operation['responses'] = get_responses(docs_data['response_models'])

    return operation


def get_responses(response_models: Responses) -> dict[str, dict]:
    responses = {}

    for status_code, response_data in response_models.items():
        if not isinstance(status_code, HTTPStatus):
            status_code = HTTPStatus(status_code)  # noqa: PLW2901

        if inspect.isclass(response_data) and issubclass(response_data, BaseModel):
            response_data = Response(model=response_data)  # noqa: PLW2901

        responses[status_code.value] = {
            'description': response_data.get('description', status_code.phrase),
            'content': {
                'application/json': {
                    'schema': response_data['model'].model_json_schema(),
                },
            },
        }

    return responses


def get_request_body(
    model_class: type[BaseModel],
    *,
    required: bool,
) -> dict:
    return {
        'required': required,
        'content': {
            'application/json': {
                'schema': model_class.model_json_schema(),
            },
        },
    }


def get_parameter_by_type(
    model_class: type[BaseModel],
    parameter_type: ParameterType,
) -> list[Parameter]:
    schema = model_class.model_json_schema()
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


def get_parameters(docs_data: ApiEndpoint) -> list[Parameter]:
    parameters = []

    if 'path_model' in docs_data:
        parameters.extend(get_parameter_by_type(docs_data['path_model'], ParameterType.PATH))

    if 'query_model' in docs_data:
        parameters.extend(get_parameter_by_type(docs_data['query_model'], ParameterType.QUERY))

    if 'header_model' in docs_data:
        parameters.extend(get_parameter_by_type(docs_data['header_model'], ParameterType.HEADER))

    if 'cookie_model' in docs_data:
        parameters.extend(get_parameter_by_type(docs_data['cookie_model'], ParameterType.COOKIE))

    return parameters
