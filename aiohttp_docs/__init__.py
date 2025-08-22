"""aiohttp docs."""

from ._decorator import docs
from ._doc_models import ApiEndpoint, Response, Responses
from ._setup import setup_docs
from ._spec_models import Contact, Info, Licence, Operation, Parameters, PathItem

__all__ = (
    'ApiEndpoint',
    'Contact',
    'Info',
    'Licence',
    'Operation',
    'Parameters',
    'PathItem',
    'Response',
    'Responses',
    'docs',
    'setup_docs',
)
