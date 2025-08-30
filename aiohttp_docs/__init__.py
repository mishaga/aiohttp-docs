"""aiohttp docs."""

from ._constants import SWAGGER_UI_DIR_PATH, SWAGGER_UI_VERSION_FILE_PATH
from ._decorator import docs
from ._doc_models import ApiEndpoint, Response, Responses
from ._enums import SwaggerLayout
from ._setup import setup_docs
from ._spec_models import Contact, Example, Info, Licence, Operation, Parameter, PathItem

__all__ = (
    'SWAGGER_UI_DIR_PATH',
    'SWAGGER_UI_VERSION_FILE_PATH',
    'ApiEndpoint',
    'Contact',
    'Example',
    'Info',
    'Licence',
    'Operation',
    'Parameter',
    'PathItem',
    'Response',
    'Responses',
    'SwaggerLayout',
    'docs',
    'setup_docs',
)
