from dataclasses import dataclass
from http import HTTPMethod
from inspect import isclass
from types import UnionType
from typing import Union, get_args, get_origin

from pydantic import BaseModel

from ._spec_models import Operation


@dataclass(slots=True, kw_only=True)
class HandlerInfo:
    method: HTTPMethod
    path: str
    operation: Operation


def get_base_model_from_annotation(annotation: type) -> type[BaseModel] | None:
    """Check if pydantic.BaseModel is inside a Union/UnionType annotation."""
    if isclass(annotation) and issubclass(annotation, BaseModel):
        return annotation

    origin = get_origin(annotation)
    if origin is Union or origin is UnionType:
        for arg in get_args(annotation):
            if isclass(arg) and issubclass(arg, BaseModel):
                return arg

    return None
