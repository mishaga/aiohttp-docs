import logging
import re
from pathlib import Path
from typing import Final

logger = logging.getLogger()

# Custom JavaScript to inject into the index.html file
INDEX_JAVASCRIPT: Final[str] = """
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


def update_index_file(index_file_path: Path) -> None:
    """Update the index.html file with custom JavaScript and proper paths.

    Args:
        index_file_path (Path): Path to the index.html file

    Raises:
        ValueError: If update fails
    """
    try:
        _update_index_file(index_file_path)
    except (OSError, re.error) as e:
        logger.exception('Failed to update index.html')
        msg = f'Index.html update failed: {e}'
        raise ValueError(msg) from e
    else:
        logger.info('Updated index.html file')


def _update_index_file(index_file_path: Path) -> None:
    content = index_file_path.read_text()

    # Fix asset paths
    content = re.sub(r'src="(\./dist/|\./|(?!{{))', 'src="$static/', content)
    content = re.sub(r'href="(\./dist/|\./|(?!{{))', 'href="$static/', content)

    # Replace the Swagger init script
    content = re.sub(
        r'<script .*/swagger-initializer.js".*</script>',
        f'<script>{INDEX_JAVASCRIPT}</script>',
        content,
    )

    # If that didn't work, try the window.onload approach
    if INDEX_JAVASCRIPT not in content:
        content = re.sub(
            r'window.onload = function\(\) {.*};$',
            INDEX_JAVASCRIPT,
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

    index_file_path.write_text(content)
