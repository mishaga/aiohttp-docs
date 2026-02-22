import logging
import re

from ._constants import README_PATH, SWAGGER_UI_RELEASE_URL_TEMPLATE

logger = logging.getLogger()


def update_readme_file(new_version: str) -> None:
    """Update the README.md file with the new Swagger UI version.

    Args:
        new_version (str): The new Swagger UI version

    Raises:
        ValueError: If update fails
    """
    try:
        updated = _update_readme_file(new_version)
    except (OSError, re.error) as e:
        logger.exception('Failed to update README')
        msg = f'README update failed: {e}'
        raise ValueError(msg) from e

    if updated:
        logger.info('Updated README file')
    else:
        logger.warning('No Swagger UI version reference found in README')


def _update_readme_file(new_version: str) -> bool:
    readme = README_PATH.read_text()

    start_tag = '<!-- SWAGGER_UI_VERSION_START -->'
    end_tag = '<!-- SWAGGER_UI_VERSION_END -->'
    pattern = rf'{start_tag}(.+){end_tag}'

    new_version_url = SWAGGER_UI_RELEASE_URL_TEMPLATE.format(version=new_version)
    new_text = f'{start_tag}[{new_version}]({new_version_url}){end_tag}'

    updated_readme, count = re.subn(pattern, new_text, readme)

    if count > 0:
        README_PATH.write_text(updated_readme)
        return True

    return False
