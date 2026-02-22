import logging
import tarfile
from pathlib import Path

logger = logging.getLogger()


def unpack_archive(tar_path: Path, target_dir: Path) -> None:
    """Unpack a tar file to a directory.

    Args:
        tar_path (Path): Path to the tar file
        target_dir (Path): Directory to extract to

    Returns:
        Path: Path to the extracted directory

    Raises:
        ValueError: If extraction fails
    """
    logger.info('Unpacking archive %s', tar_path)

    try:
        _unpack_archive(tar_path, target_dir)
    except (OSError, tarfile.TarError) as e:
        logger.exception('Failed to extract %s', tar_path)
        msg = f'Extraction failed: {e}'
        raise ValueError(msg) from e
    else:
        logger.info('Archive unpacked to %s', target_dir)


def _unpack_archive(tar_path: Path, target_dir: Path) -> None:
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
