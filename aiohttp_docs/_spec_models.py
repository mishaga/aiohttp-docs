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


class OpenApiSpecification(TypedDict):
    openapi: str
    info: Info
    paths: dict[str, PathItem]
