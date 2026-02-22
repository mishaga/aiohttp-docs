import logging
from pathlib import Path

import aiohttp

from ._constants import GITHUB_DOWNLOAD_FILE_TIMEOUT

logger = logging.getLogger()


async def download_archive(url: str, target_path: Path) -> None:
    """Download a file from a URL to the specified path.

    Args:
        url (str): The URL to download from
        target_path (Path): The path to save the file to

    Raises:
        ValueError: If download fails
    """
    logger.info('Downloading archive from %s', url)

    try:
        await _download_archive(url, target_path)
    except (OSError, aiohttp.ClientResponseError) as e:
        logger.exception('Failed to download %s', url)
        msg = f'Download failed: {e}'
        raise ValueError(msg) from e
    else:
        logger.info('Archive downloaded')


async def _download_archive(url: str, target_path: Path) -> None:
    async with (
        aiohttp.ClientSession() as session,
        session.get(url=url, timeout=GITHUB_DOWNLOAD_FILE_TIMEOUT) as resp,
    ):
        resp.raise_for_status()
        target_path.write_bytes(await resp.read())  # noqa: ASYNC240
