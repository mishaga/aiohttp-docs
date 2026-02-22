import json
import logging

import aiohttp

from ._constants import GITHUB_API_REQUEST_TIMEOUT, SWAGGER_UI_LATEST_RELEASE_API_URL

logger = logging.getLogger()


async def get_latest_swagger_version() -> str:
    """Get the latest version of Swagger UI.

    Returns:
        str: The latest Swagger UI version
    """
    try:
        version = await _get_latest_swagger_version()
    except (json.JSONDecodeError, KeyError) as e:
        logger.exception('Failed to fetch latest release')
        msg = f'Could not determine latest version: {e}'
        raise ValueError(msg) from e
    else:
        logger.info('Latest Swagger UI version: %s', version)

    return version


async def _get_latest_swagger_version() -> str:
    """Get the latest version of a GitHub repository using the GitHub API.

    Returns:
        str: The latest version tag

    Raises:
        ValueError: If unable to get the latest version
    """
    logger.info('Checking latest release from %s', SWAGGER_UI_LATEST_RELEASE_API_URL)

    async with (
        aiohttp.ClientSession() as session,
        session.get(url=SWAGGER_UI_LATEST_RELEASE_API_URL, timeout=GITHUB_API_REQUEST_TIMEOUT) as resp,
    ):
        # ... raise for status
        latest = await resp.json()

    tag: str | None = latest.get('tag_name')

    if not tag:
        msg = 'No tag found in GitHub API response'
        raise ValueError(msg)

    return tag
