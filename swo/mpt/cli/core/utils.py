from glob import glob
from pathlib import Path
from typing import Any


def set_dict_value(original_dict: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    path_list = path.split(".", 1)

    if len(path_list) == 1:
        original_dict[path_list[0]] = value
    else:
        current, next_path = path_list[0], path_list[-1]
        if current in original_dict:
            original_dict[current] = set_dict_value(original_dict[current], next_path, value)
        else:
            original_dict[current] = set_dict_value({}, next_path, value)

    return original_dict


def get_files_path(files_path: list[str]) -> list[str]:
    file_paths = []

    for file_path in files_path:
        path = Path(file_path)
        if path.is_file():
            file_paths.append(file_path)
        elif path.is_dir():
            file_paths.extend(glob(str(path / "*")))
        else:
            file_paths.extend(glob(file_path))

    return list(filter(lambda p: p.endswith(".xlsx"), file_paths))
