"""OpenAPI specification models.

https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md

https://editor-next.swagger.io
"""

from typing import Any, Required, TypedDict

from ._enums import ParameterType


class Licence(TypedDict, total=False):
    name: Required[str]
    identifier: str
    url: str


class Contact(TypedDict, total=False):
    name: str
    url: str
    email: str


class Info(TypedDict, total=False):
    title: Required[str]
    summary: str
    description: str
    termsOfService: str
    contact: Contact
    licence: Licence
    version: Required[str]


class ServerVariable(TypedDict, total=False):
    enum: list[str]
    default: Required[str]
    description: str


class Server(TypedDict, total=False):
    url: Required[str]
    description: str
    variables: dict[str, ServerVariable]


class Example(TypedDict, total=False):
    summary: str
    description: str
    value: Any
    externalValue: Any


Parameter = TypedDict(
    'Parameter',
    {
        'name': Required[str],
        'in': Required[ParameterType],
        'description': str,
        'required': Required[bool],
        'deprecated': bool,
        'examples': dict[str, Example],
        'schema': dict,
    },
    total=False,
)


class Operation(TypedDict, total=False):
    tags: list[str]
    summary: str
    description: str
    deprecated: bool
    parameters: list[Parameter]
    requestBody: dict
    responses: dict[str, dict]


class PathItem(TypedDict, total=False):
    get: Operation
    put: Operation
    post: Operation
    delete: Operation
    options: Operation
    head: Operation
    patch: Operation
    trace: Operation


class Components(TypedDict, total=False):
    schemas: dict[str, dict]
    responses: dict[str, dict]
    parameters: dict[str, dict]
    examples: dict[str, dict]
    requestBodies: dict[str, dict]
    headers: dict[str, dict]
    securitySchemes: dict[str, dict]
    links: dict[str, dict]
    callbacks: dict[str, dict]
    pathItems: dict[str, dict]


class OpenApiSpecification(TypedDict, total=False):
    openapi: Required[str]
    info: Required[Info]
    paths: Required[dict[str, PathItem]]
    servers: list[Server]
    components: Components
