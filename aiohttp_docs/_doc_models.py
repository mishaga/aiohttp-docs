from http import HTTPStatus
from typing import Required, TypedDict

from pydantic import BaseModel

type Responses = dict[HTTPStatus | int, Response | type[BaseModel] | None]


class Response(TypedDict, total=False):
    model: Required[type[BaseModel] | None]
    description: str


class ApiEndpoint(TypedDict, total=False):
    tags: list[str]
    summary: str
    description: str
    deprecated: bool
    path_model: type[BaseModel]
    query_model: type[BaseModel]
    header_model: type[BaseModel]
    cookie_model: type[BaseModel]
    body_model: type[BaseModel]
    response_models: Responses
