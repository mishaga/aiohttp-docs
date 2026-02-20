from pathlib import Path
from typing import Final

OPENAPI_SPEC_VERSION: Final[str] = '3.1.2'

DOCS_ATTR_NAME: Final[str] = '_openapi_docs'

SWAGGER_UI_DIR_PATH = Path(__file__).parent / 'swagger'
SWAGGER_UI_VERSION_FILE_PATH = SWAGGER_UI_DIR_PATH / 'VERSION'

ROUTE_NAME_STATIC: Final[str] = 'docs.swagger.static'
ROUTE_NAME_SPEC_VIEW: Final[str] = 'docs.swagger.spec'
ROUTE_NAME_SWAGGER_VIEW: Final[str] = 'docs.swagger.ui'
