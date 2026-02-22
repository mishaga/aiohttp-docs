import logging

from aiohttp_docs._constants import SWAGGER_UI_VERSION_FILE_PATH

logger = logging.getLogger()


def get_current_swagger_version() -> str:
    """Get the current Swagger UI version from the VERSION file.

    Returns:
        str: The current Swagger UI version
    """
    try:
        version = SWAGGER_UI_VERSION_FILE_PATH.read_text().strip()
    except (OSError, FileNotFoundError) as e:
        version = 'unknown'
        logger.warning('Could not read current version: %s', e)
    else:
        logger.info('Current Swagger UI version: %s', version)

    return version
