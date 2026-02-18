from glob import glob
from pathlib import Path


def get_files_path(files_path: list[str]) -> list[str]:
    """Get all .xlsx file paths from a list of files or directories.

    Args:
        files_path: List of file or directory paths.

    Returns:
        List of .xlsx file paths found in the given paths.

    """
    file_paths = []

    for file_path in files_path:
        path = Path(file_path)
        if path.is_file():
            file_paths.append(file_path)
        elif path.is_dir():
            file_paths.extend(glob(str(path / "*")))  # noqa: PTH207
        else:
            file_paths.extend(glob(file_path))  # noqa: PTH207

    return [path_entry for path_entry in file_paths if path_entry.endswith(".xlsx")]
