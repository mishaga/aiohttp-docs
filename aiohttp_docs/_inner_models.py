from dataclasses import dataclass
from http import HTTPMethod

from ._spec_models import Operation


@dataclass(slots=True, kw_only=True)
class RouteInfo:
    method: HTTPMethod
    path: str
    operation: Operation
