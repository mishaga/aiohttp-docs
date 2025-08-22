from http import HTTPStatus
from typing import Required, TypedDict

from pydantic import BaseModel

type Responses = dict[HTTPStatus | int, Response | type[BaseModel]]


class Response(TypedDict, total=False):
    model: Required[type[BaseModel]]
    description: str


class ApiEndpoint(TypedDict, total=False):
    tags: list[str]
    summary: str
    description: str
    body_model: type[BaseModel]
    query_model: type[BaseModel]
    response_models: Responses
