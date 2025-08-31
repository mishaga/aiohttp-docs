"""Script to update the Swagger UI files to the latest version.

This script:
1. Checks the current version of Swagger UI
2. Gets the latest version of Swagger UI from GitHub
3. Downloads and extracts the latest version if needed
4. Updates the UI files in the project
5. Updates version information in the README and VERSION file
"""

import logging
import sys
import tempfile
from pathlib import Path

from aiohttp_docs import SWAGGER_UI_DIR_PATH
from tools.update_swagger_ui._archive import download_file, unpack_dist_folder
from tools.update_swagger_ui._constants import SWAGGER_UI_REPO
from tools.update_swagger_ui._directory import prepare_swagger_ui_directory
from tools.update_swagger_ui._update_files import update_current_version, update_index_html, update_readme
from tools.update_swagger_ui._versions import get_current_version, get_latest_version

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()


def download_and_update_swagger_ui(version: str) -> None:
    """Download and update Swagger UI files to the specified version.

    Args:
        version (str): The version to download

    Raises:
        ValueError: If download or update fails
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tar_path = temp_path / f'{version}.tar.gz'

        # download archive
        download_file(
            url=f'https://github.com/{SWAGGER_UI_REPO}/archive/{version}.tar.gz',
            target_path=tar_path,
        )

        # ensure destination folder exists and is empty
        prepare_swagger_ui_directory(path=SWAGGER_UI_DIR_PATH)

        # extract archive
        unpack_dist_folder(
            tar_path=tar_path,
            target_dir=SWAGGER_UI_DIR_PATH,
        )

        # update index.html and version references
        update_index_html(SWAGGER_UI_DIR_PATH / 'index.html')
        update_current_version(version)
        update_readme(version)

    logger.info('Successfully updated Swagger UI to version %s', version)


def run() -> None:
    """Compare current and GitHub versions of Swagger UI, update if needed."""
    # Get current and latest versions
    current_version = get_current_version()
    logger.info('Current Swagger UI version: %s', current_version)

    latest_version = get_latest_version()
    logger.info('Latest Swagger UI version: %s', latest_version)

    # Check if update is needed
    if current_version == latest_version:
        logger.info('Swagger UI is already up to date (%s)', latest_version)
        return

    # Download and update if needed
    logger.info('Updating Swagger UI from %s to %s', current_version, latest_version)
    download_and_update_swagger_ui(latest_version)


def main() -> int:
    """Main function to update Swagger UI.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        run()
    except Exception:
        logger.exception('Failed to update Swagger UI')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
