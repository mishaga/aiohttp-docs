import json
import logging

import requests

from aiohttp_docs import SWAGGER_UI_VERSION_FILE_PATH

from ._constants import GITHUB_API_TIMEOUT, SWAGGER_UI_REPO

logger = logging.getLogger()


def get_current_version() -> str:
    """Get the current Swagger UI version from the VERSION file.

    Returns:
        str: The current Swagger UI version
    """
    try:
        return SWAGGER_UI_VERSION_FILE_PATH.read_text().strip()
    except (OSError, FileNotFoundError) as e:
        logger.warning('Could not read current version: %s', e)
        return 'unknown'


def get_latest_version() -> str:
    """Get the latest version of Swagger UI.

    Returns:
        str: The latest Swagger UI version
    """
    try:
        return _detect_latest_release(SWAGGER_UI_REPO)
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        logger.exception('Failed to fetch latest release')
        msg = f'Could not determine latest version: {e}'
        raise ValueError(msg) from e


def _detect_latest_release(repo: str) -> str:
    """Get the latest version of a GitHub repository using the GitHub API.

    Args:
        repo (str): GitHub repository in the format 'owner/repo'

    Returns:
        str: The latest version tag

    Raises:
        ValueError: If unable to get the latest version
    """
    url = f'https://api.github.com/repos/{repo}/releases/latest'
    logger.info('Checking latest release from %s', url)

    resp = requests.get(url, timeout=GITHUB_API_TIMEOUT)
    resp.raise_for_status()
    latest = resp.json()
    tag: str | None = latest.get('tag_name')

    if not tag:
        msg = 'No tag found in GitHub API response'
        raise ValueError(msg)

    return tag
