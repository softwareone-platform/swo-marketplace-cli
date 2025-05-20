import re
from collections.abc import Generator
from re import Pattern
from typing import Any

from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler, SheetData
from swo.mpt.cli.core.stats import StatsCollector


# TODO: add typehints here
def find_first(func, iterable, default=None):
    return next(filter(func, iterable), default)


def find_values_by_pattern(
    pattern: Pattern[str], values: SheetData
) -> Generator[tuple[str, Any], None, None]:
    for key, value in values.items():
        if re.match(pattern, key):
            yield key, value


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


def set_value(column_name: str, values: SheetData, value: str) -> SheetData:
    values[column_name]["value"] = value
    return values


def add_or_create_error(
    file_handler: ExcelFileHandler, sheet_name: str, sheet_data: SheetData, exception: Exception
):
    try:
        coordinate = sheet_data["Error"]["coordinate"]
        column_letter = coordinate[0]
        row_number = coordinate[1]
    except KeyError:
        column_letter = file_handler.get_sheet_next_column(sheet_name)
        row_number = next(iter(sheet_data.values()))["coordinate"][1]
        file_handler.write([{sheet_name: {f"{column_letter}1": "Error"}}])

    file_handler.write([{sheet_name: {f"{column_letter}{row_number}": str(exception)}}])


def status_step_text(stats: StatsCollector, tab_name: str) -> str:
    results = stats.tabs[tab_name]

    return (
        f"[green]{results['synced']}[/green] / "
        f"[red bold]{results['error']}[/red bold] / "
        f"[white bold]{results['skipped']}[/white bold] / "
        f"[blue]{results['total']}[/blue]"
    )
