import logging
import shutil
from pathlib import Path

logger = logging.getLogger()


def prepare_swagger_ui_directory(path: Path) -> None:
    """Ensure a clean directory exists (removes it if it exists, then creates it).

    Args:
        path (Path): Directory path

    Raises:
        ValueError: If directory creation fails
    """
    try:
        _prepare_swagger_ui_directory(path)
    except OSError as e:
        logger.exception('Failed to prepare directory %s', path)
        msg = f'Directory preparation failed: {e}'
        raise ValueError(msg) from e


def _prepare_swagger_ui_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
        logger.info('Cleaned directory %s', path)

    path.mkdir(parents=True, exist_ok=True)
