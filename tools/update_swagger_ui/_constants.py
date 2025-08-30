from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
README_PATH = PROJECT_DIR / 'README.md'
SWAGGER_UI_REPO = 'swagger-api/swagger-ui'

GITHUB_API_TIMEOUT = 120  # seconds
REQUEST_TIMEOUT = 300  # seconds
