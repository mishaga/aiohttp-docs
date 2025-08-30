import logging
import re
from pathlib import Path

from aiohttp_docs import SWAGGER_UI_VERSION_FILE_PATH

from ._constants import README_PATH

logger = logging.getLogger()

# Custom JavaScript to inject into the index.html file
INDEX_JAVASCRIPT = """
    window.onload = function() {
      // Begin Swagger UI call region
      window.ui = SwaggerUIBundle({
        url: "$path",
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "$layout",
      });
      // End Swagger UI call region
    };
  """


def update_index_html(index_path: Path) -> None:
    """Update the index.html file with custom JavaScript and proper paths.

    Args:
        index_path (Path): Path to the index.html file

    Raises:
        ValueError: If update fails
    """
    try:
        _update_index_file(index_path)
    except (OSError, re.error) as e:
        logger.exception('Failed to update index.html')
        msg = f'Index.html update failed: {e}'
        raise ValueError(msg) from e

    logger.info('Updated %s', index_path)


def update_readme(version: str) -> None:
    """Update the README.md file with the new Swagger UI version.

    Args:
        version (str): The new Swagger UI version

    Raises:
        ValueError: If update fails
    """
    try:
        _update_readme(version)
    except (OSError, re.error) as e:
        logger.exception('Failed to update README')
        msg = f'README update failed: {e}'
        raise ValueError(msg) from e


def update_current_version(version: str) -> None:
    """Update the VERSION file with the new Swagger UI version.

    Args:
        version (str): The new Swagger UI version

    Raises:
        ValueError: If update fails
    """
    try:
        SWAGGER_UI_VERSION_FILE_PATH.write_text(version)
    except OSError as e:
        logger.exception('Failed to update VERSION file')
        msg = f'VERSION file update failed: {e}'
        raise ValueError(msg) from e

    logger.info('Updated VERSION file to %s', version)


def _update_index_file(index_path: Path) -> None:
    html = index_path.read_text()

    # Fix asset paths
    html = re.sub(r'src="(\./dist/|\./|(?!{{))', 'src="$static/', html)
    html = re.sub(r'href="(\./dist/|\./|(?!{{))', 'href="$static/', html)

    # Replace the Swagger initializer script
    html = re.sub(
        r'<script .*/swagger-initializer.js".*</script>',
        f'<script>{INDEX_JAVASCRIPT}</script>',
        html,
    )

    # If that didn't work, try the window.onload approach
    if INDEX_JAVASCRIPT not in html:
        html = re.sub(
            r'window.onload = function\(\) {.*};$',
            INDEX_JAVASCRIPT,
            html,
            flags=re.MULTILINE | re.DOTALL,
        )

    index_path.write_text(html)


def _update_readme(version: str) -> None:
    readme = README_PATH.read_text()

    start_tag = '<!-- SWAGGER_UI_VERSION_START -->'
    end_tag = '<!-- SWAGGER_UI_VERSION_END -->'
    pattern = rf'{start_tag}(.+){end_tag}'
    new_text = f'{start_tag}[{version}](https://github.com/swagger-api/swagger-ui/releases/tag/{version}){end_tag}'

    updated_readme, count = re.subn(pattern, new_text, readme)

    if count > 0:
        README_PATH.write_text(updated_readme)
        logger.info('Updated README with Swagger UI version %s', version)
    else:
        logger.warning('No Swagger UI version reference found in README')
