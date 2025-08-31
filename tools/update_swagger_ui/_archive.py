import logging
import tarfile
from pathlib import Path

import requests

from ._constants import REQUEST_TIMEOUT

logger = logging.getLogger()


def download_file(url: str, target_path: Path) -> None:
    """Download a file from a URL to the specified path.

    Args:
        url (str): The URL to download from
        target_path (Path): The path to save the file to

    Raises:
        ValueError: If download fails
    """
    logger.info('Downloading archive from %s', url)

    try:
        _download_file(url, target_path)
    except (OSError, requests.RequestException) as e:
        logger.exception('Failed to download %s', url)
        msg = f'Download failed: {e}'
        raise ValueError(msg) from e

    logger.info('Downloaded %s to %s', url, target_path)


def unpack_dist_folder(tar_path: Path, target_dir: Path) -> None:
    """Unpack a tar file to a directory.

    Args:
        tar_path (Path): Path to the tar file
        target_dir (Path): Directory to extract to

    Returns:
        Path: Path to the extracted directory

    Raises:
        ValueError: If extraction fails
    """
    logger.info('Extracting %s', tar_path)

    try:
        _unpack_dist_folder(tar_path, target_dir)
    except (OSError, tarfile.TarError) as e:
        logger.exception('Failed to extract %s', tar_path)
        msg = f'Extraction failed: {e}'
        raise ValueError(msg) from e


def _download_file(url: str, target_path: Path) -> None:
    resp = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    target_path.write_bytes(resp.content)


def _unpack_dist_folder(tar_path: Path, target_dir: Path) -> None:
    with tarfile.open(tar_path) as tar_file:
        all_members = tar_file.getmembers()
        root_folder = all_members[0]
        prefix = f'{root_folder.name}/dist/'

        members = []
        for member in all_members:
            if member.name.startswith(prefix):
                m = tar_file.getmember(member.name)
                m.name = member.name.removeprefix(prefix)
                members.append(m)

        tar_file.extractall(  # noqa: S202 Uses of `tarfile.extractall()`
            path=target_dir,
            members=members,
            filter='fully_trusted',
        )
