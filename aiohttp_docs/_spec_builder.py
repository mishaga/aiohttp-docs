import inspect
from collections import defaultdict
from http import HTTPMethod, HTTPStatus
from typing import Any

from aiohttp import web
from aiohttp.typedefs import Handler
from pydantic import BaseModel

from ._constants import DOCS_ATTR_NAME
from ._doc_models import ApiEndpoint, Response, Responses
from ._spec_models import Info, OpenApiSpecification


def build_openapi_spec(
    app: web.Application,
    *,
    info: Info,
) -> OpenApiSpecification:
    """Build OpenAPI 3.1 specification from application routes."""
    paths = defaultdict(dict)
    for route in app.router.routes():  # ... extract to a func
        if inspect.isfunction(route.handler) and hasattr(route.handler, DOCS_ATTR_NAME):
            path_info = extract_path_info(route.handler)
            path_pattern = route.resource.canonical
            method = route.method.lower()
            paths[path_pattern][method] = path_info
        elif inspect.isclass(route.handler):
            for method in HTTPMethod:
                method = method.lower()  # noqa: PLW2901
                handler = getattr(route.handler, method, None)
                if handler and hasattr(handler, DOCS_ATTR_NAME):
                    path_info = extract_path_info(handler)
                    path_pattern = route.resource.canonical
                    paths[path_pattern][method] = path_info

    return OpenApiSpecification(
        openapi='3.1.0',
        info=info,
        paths=paths,
    )


def extract_path_info(handler: Handler) -> dict[str, Any] | None:
    """Extract OpenAPI path information from a documented route."""
    path_info: dict[str, Any] = {}
    docs_data: ApiEndpoint = getattr(handler, DOCS_ATTR_NAME)
    docstring = inspect.getdoc(handler)

    if 'tags' in docs_data:
        path_info['tags'] = docs_data['tags']

    if 'summary' in docs_data:
        path_info['summary'] = docs_data['summary']

    if 'description' in docs_data:
        path_info['description'] = docs_data['description']
    elif docstring:
        path_info['description'] = docstring

    if 'response_models' in docs_data:
        path_info['responses'] = get_responses(docs_data['response_models'])

    if 'body_model' in docs_data:
        path_info['requestBody'] = get_request_body(docs_data['body_model'])

    if 'query_model' in docs_data:
        path_info['parameters'] = get_query_parameters(docs_data['query_model'])

    return path_info


def get_responses(response_models: Responses) -> dict[str, Any]:
    responses = {}

    for status_code, response_data in response_models.items():
        if not isinstance(status_code, HTTPStatus):
            status_code = HTTPStatus(status_code)  # noqa: PLW2901

        if issubclass(response_data, BaseModel):
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


def get_request_body(model_class: type[BaseModel]) -> dict:
    return {
        'required': True,
        'content': {
            'application/json': {
                'schema': model_class.model_json_schema(),
            },
        },
    }


def get_query_parameters(model_class: type[BaseModel]) -> list[dict[str, Any]]:
    return [
        {
            'name': field_name,
            'in': 'query',
            'required': field_info.is_required(),
            'schema': model_class.model_json_schema(),
        }
        for field_name, field_info in model_class.model_fields.items()
    ]
