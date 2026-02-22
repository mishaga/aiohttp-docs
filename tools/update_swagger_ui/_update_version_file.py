import logging

from aiohttp_docs._constants import SWAGGER_UI_VERSION_FILE_PATH

logger = logging.getLogger()


def update_version_file(new_version: str) -> None:
    """Update the VERSION file with the new Swagger UI version.

    Args:
        new_version (str): The new Swagger UI version

    Raises:
        ValueError: If update fails
    """
    try:
        SWAGGER_UI_VERSION_FILE_PATH.write_text(new_version)
    except OSError as e:
        logger.exception('Failed to update VERSION file')
        msg = f'VERSION file update failed: {e}'
        raise ValueError(msg) from e
    else:
        logger.info('Updated VERSION file')
