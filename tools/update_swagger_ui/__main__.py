"""Script to update the Swagger UI files to the latest version.

This script:
1. Checks the current version of Swagger UI
2. Gets the latest version of Swagger UI from GitHub
3. Downloads and extracts the latest version if needed
4. Updates the UI files in the project
5. Updates version information in the README and VERSION file
"""

import asyncio
import logging
import sys
import tempfile
from pathlib import Path

from aiohttp_docs._constants import SWAGGER_UI_DIR_PATH

from ._constants import SWAGGER_UI_ARCHIVE_URL_TEMPLATE
from ._download_archive import download_archive
from ._get_current_swagger_version import get_current_swagger_version
from ._get_latest_swagger_version import get_latest_swagger_version
from ._prepare_swagger_ui_directory import prepare_swagger_ui_directory
from ._unpack_archive import unpack_archive
from ._update_index_file import update_index_file
from ._update_readme_file import update_readme_file
from ._update_version_file import update_version_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()


async def download_and_update_swagger_ui(current_version: str, new_version: str) -> None:
    """Download and update Swagger UI files to the specified version.

    Args:
        current_version (str): The current version of Swagger UI stored in the `aiohttp_docs/swagger` directory
        new_version (str): The version to update to

    Raises:
        ValueError: If download or update fails
    """
    logger.info('Updating Swagger UI from %s to %s', current_version, new_version)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tar_path = temp_path / f'{new_version}.tar.gz'

        # download archive
        await download_archive(
            url=SWAGGER_UI_ARCHIVE_URL_TEMPLATE.format(version=new_version),
            target_path=tar_path,
        )

        # ensure destination folder exists and is empty
        prepare_swagger_ui_directory(
            path=SWAGGER_UI_DIR_PATH,
        )

        # extract archive
        unpack_archive(
            tar_path=tar_path,
            target_dir=SWAGGER_UI_DIR_PATH,
        )

    # update index.html and version references
    update_index_file(SWAGGER_UI_DIR_PATH / 'index.html')
    update_version_file(new_version)
    update_readme_file(new_version)

    logger.info('Successfully updated Swagger UI to version %s', new_version)


async def run() -> None:
    """Compare current and GitHub versions of Swagger UI, update if needed."""
    # Get current and latest versions
    current_version = get_current_swagger_version()
    latest_version = await get_latest_swagger_version()

    # Check if update is needed
    if current_version == latest_version:
        logger.info('Swagger UI is already up to date (%s)', latest_version)
        return

    # Download and update swagger UI
    await download_and_update_swagger_ui(
        current_version=current_version,
        new_version=latest_version,
    )


def main() -> int:
    """Main function to update Swagger UI.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        asyncio.run(run())
    except Exception:
        logger.exception('Failed to update Swagger UI')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
