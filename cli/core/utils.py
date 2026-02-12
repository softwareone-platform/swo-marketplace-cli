from glob import glob
from pathlib import Path
from typing import Any


def set_dict_value(original_dict: dict[str, Any], path: str, new_value: Any) -> dict[str, Any]:
    """Set a value in a nested dictionary using a dot-separated path.

    Args:
        original_dict: The dictionary to update.
        path: Dot-separated string representing the nested keys.
        new_value: The value to set at the specified path.

    Returns:
        The updated dictionary with the value set at the given path.

    """
    path_list = path.split(".", 1)
    if len(path_list) == 1:
        original_dict[path_list[0]] = new_value
    else:
        current, next_path = path_list[0], path_list[-1]
        if current in original_dict:
            original_dict[current] = set_dict_value(original_dict[current], next_path, new_value)
        else:
            original_dict[current] = set_dict_value({}, next_path, new_value)

    return original_dict


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

    return list(filter(lambda p: p.endswith(".xlsx"), file_paths))
