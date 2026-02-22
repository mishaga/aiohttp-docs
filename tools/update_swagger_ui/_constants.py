from pathlib import Path
from typing import Final

CURRENT_DIR: Final[Path] = Path(__file__).resolve().parent
PROJECT_DIR: Final[Path] = CURRENT_DIR.parent.parent
README_PATH: Final[Path] = PROJECT_DIR / 'README.md'

SWAGGER_UI_REPO_NAME: Final[str] = 'swagger-api/swagger-ui'
SWAGGER_UI_REPO_URL: Final[str] = f'https://github.com/{SWAGGER_UI_REPO_NAME}'
SWAGGER_UI_LATEST_RELEASE_API_URL: Final[str] = f'https://api.github.com/repos/{SWAGGER_UI_REPO_NAME}/releases/latest'
SWAGGER_UI_ARCHIVE_URL_TEMPLATE: Final[str] = f'{SWAGGER_UI_REPO_URL}/archive/{{version}}.tar.gz'
SWAGGER_UI_RELEASE_URL_TEMPLATE: Final[str] = f'{SWAGGER_UI_REPO_URL}/releases/tag/{{version}}'

GITHUB_API_REQUEST_TIMEOUT: Final[int] = 10  # seconds
GITHUB_DOWNLOAD_FILE_TIMEOUT: Final[int] = 30  # seconds
