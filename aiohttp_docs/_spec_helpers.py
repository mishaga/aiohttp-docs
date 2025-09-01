from dataclasses import dataclass
from http import HTTPMethod

from ._spec_models import Operation


@dataclass(slots=True, kw_only=True)
class HandlerInfo:
    method: HTTPMethod
    path: str
    operation: Operation
