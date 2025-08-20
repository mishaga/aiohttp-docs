"""aiohttp docs."""

from ._decorator import docs
from ._types import DocParams, ResponseData, ResponsesDict
from ._spec import OpenapiJsonSpec, OpenapiYamlSpec

__all__ = (
    'DocParams',
    'OpenapiJsonSpec',
    'OpenapiYamlSpec',
    'ResponseData',
    'ResponsesDict',
    'docs',
)
