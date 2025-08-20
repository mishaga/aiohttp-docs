from typing import TypedDict, Required, TypeAlias
from http import HTTPStatus

from pydantic import BaseModel


class ResponseData(TypedDict, total=False):
    model: Required[type[BaseModel]]
    description: str


ResponsesDict: TypeAlias = dict[HTTPStatus | int, ResponseData | type[BaseModel]]


class DocParams(TypedDict, total=False):
    tags: list[str]
    summary: str
    description: str
    body_model: type[BaseModel]
    query_model: type[BaseModel]
    response_models: ResponsesDict
