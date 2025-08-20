from aiohttp import web
from aiohttp.typedefs import Handler
from http import HTTPStatus, HTTPMethod
from typing import Any
import inspect

from pydantic import BaseModel
import yaml

from ._constants import DOCS_ATTR_NAME
from ._types import DocParams, ResponseData, ResponsesDict


class OpenapiJsonSpec(web.View):
    """OpenAPI specification endpoint, returns JSON."""

    async def get(self) -> web.Response:
        """Generate and return OpenAPI specification in JSON format."""
        spec = build_openapi_spec(self.request.app)
        return web.json_response(spec)


class OpenapiYamlSpec(web.View):
    """OpenAPI specification endpoint, returns YAML."""

    async def get(self) -> web.Response:
        """Generate and return OpenAPI specification in YAML format."""
        spec = build_openapi_spec(self.request.app)
        return web.Response(
            text=yaml.dump(spec),
        )


def build_openapi_spec(app: web.Application) -> dict[str, Any]:
    """Build OpenAPI 3.1 specification from application routes."""
    spec: dict[str, Any] = {
        'openapi': '3.1.0',
        'info': {
            'title': 'API Documentation',
            'version': '1.0.0',
            'description': 'Auto-generated API documentation',
        },
        'paths': {},
        'components': {
            'schemas': {},
        },
    }

    for route in app.router.routes():
        if inspect.isfunction(route.handler) and hasattr(route.handler, DOCS_ATTR_NAME):
            path_info = extract_path_info(route.handler)
            path_pattern = route.resource.canonical
            method = route.method.lower()

            if path_pattern not in spec['paths']:
                spec['paths'][path_pattern] = {}

            spec['paths'][path_pattern][method] = path_info
        elif inspect.isclass(route.handler):
            for method in HTTPMethod:
                method = method.lower()
                handler = getattr(route.handler, method, None)
                if handler and hasattr(handler, DOCS_ATTR_NAME):
                    path_info = extract_path_info(handler)
                    path_pattern = route.resource.canonical

                    if path_pattern not in spec['paths']:
                        spec['paths'][path_pattern] = {}

                    spec['paths'][path_pattern][method] = path_info

    return spec


def extract_path_info(handler: Handler) -> dict[str, Any] | None:
    """Extract OpenAPI path information from a documented route."""
    path_info: dict[str, Any] = {}
    docs_data: DocParams = getattr(handler, DOCS_ATTR_NAME)

    if 'tags' in docs_data:
        path_info['tags'] = docs_data['tags']

    if 'summary' in docs_data:
        path_info['summary'] = docs_data['summary']

    if 'description' in docs_data:
        path_info['description'] = docs_data['description']

    if 'response_models' in docs_data:
        path_info['responses'] = get_responses(docs_data['response_models'])

    if 'body_model' in docs_data:
        path_info['requestBody'] = get_request_body(docs_data['body_model'])

    if 'query_model' in docs_data:
        path_info['parameters'] = get_query_parameters(docs_data['query_model'])

    return path_info


def get_responses(response_models: ResponsesDict) -> dict[str, Any]:
    responses = {}

    for status_code, response_data in response_models.items():
        print()
        print()
        print()
        print(status_code, response_data)

        if issubclass(response_data, BaseModel):
            print('YES')
            response_data = ResponseData(model=response_data)
        else:
            print('NO')

        if not isinstance(status_code, HTTPStatus):
            status_code = HTTPStatus(status_code)
        status_str = str(status_code.value)

        if 'description' in response_data:
            description = response_data['description']
        else:
            description = status_code.phrase

        responses[status_str] = {
            'description': description,
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
