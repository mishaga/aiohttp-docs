import logging
import shutil
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
    try:
        _download_file(url, target_path)
    except (OSError, requests.RequestException) as e:
        logger.exception('Failed to download %s', url)
        msg = f'Download failed: {e}'
        raise ValueError(msg) from e

    logger.info('Downloaded %s to %s', url, target_path)


def unpack_archive(tar_path: Path, target_dir: Path) -> Path:
    """Unpack a tar file to a directory.

    Args:
        tar_path (Path): Path to the tar file
        target_dir (Path): Directory to extract to

    Returns:
        Path: Path to the extracted directory

    Raises:
        ValueError: If extraction fails
    """
    try:
        return _unpack_archive(tar_path, target_dir)
    except (OSError, tarfile.TarError) as e:
        logger.exception('Failed to extract %s', tar_path)
        msg = f'Extraction failed: {e}'
        raise ValueError(msg) from e


def copy_dist_files(dist_dir: Path, destination_dir: Path) -> None:
    """Copy distribution files to the destination directory.

    Args:
        dist_dir (Path): Source directory with distribution files
        destination_dir (Path): Destination directory

    Raises:
        ValueError: If copy fails
    """
    try:
        _copy_dist_files(dist_dir, destination_dir)
    except (OSError, shutil.Error) as e:
        logger.exception('Failed to copy distribution files')
        msg = f'File copy failed: {e}'
        raise ValueError(msg) from e

    logger.info('Copied files from %s to %s', dist_dir, destination_dir)


def _download_file(url: str, target_path: Path) -> None:
    with requests.get(url, stream=True, timeout=REQUEST_TIMEOUT) as resp:
        resp.raise_for_status()
        with target_path.open('wb') as f:
            shutil.copyfileobj(resp.raw, f)


def _unpack_archive(tar_path: Path, target_dir: Path) -> Path:
    with tarfile.open(tar_path) as tar_file:
        tar_file.extractall(path=target_dir, filter='fully_trusted')  # noqa: S202
        extract_dirname = tar_file.getnames()[0]
    return target_dir / extract_dirname


def _copy_dist_files(dist_dir: Path, destination_dir: Path) -> None:
    for path in dist_dir.glob('**/*'):
        if path.is_file():
            dst_path = destination_dir / path.relative_to(dist_dir)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dst_path)
            logger.debug('Copied %s to %s', path, dst_path)
