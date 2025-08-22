"""OpenAPI specification models.

https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md

https://editor-next.swagger.io
"""

from typing import Literal, Required, TypedDict


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


class Operation(TypedDict, total=False):
    tags: list[str]
    summary: str
    description: str


Parameters = TypedDict(
    'Parameters',
    {
        'name': Required[str],
        'in': Required[Literal['query', 'header', 'path', 'cookie']],
        'description': str,
        'required': Required[bool],
        'deprecated': bool,
        'allowEmptyValue': bool,
    },
    total=False,
)


class PathItem(TypedDict, total=False):
    summary: str
    description: str
    get: Operation
    put: Operation
    post: Operation
    delete: Operation
    options: Operation
    head: Operation
    patch: Operation
    trace: Operation
    parameters: Parameters


class OpenApiSpecification(TypedDict):
    openapi: Literal['3.1.0']
    info: Info
    paths: dict[str, PathItem]
