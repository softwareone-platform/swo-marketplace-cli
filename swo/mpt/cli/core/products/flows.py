import os
from pathlib import Path

from openpyxl import load_workbook  # type: ignore
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore
from swo.mpt.cli.core.errors import FileNotExistsError
from swo.mpt.cli.core.products.constants import (
    REQUIRED_FIELDS_BY_TAB,
    REQUIRED_FIELDS_WITH_VALUES_BY_TAB,
    REQUIRED_TABS,
    TAB_GENERAL,
)
from swo.mpt.cli.core.stats import StatsCollector


def get_definition_file(path: str) -> Path:
    """
    Returns product definition file path. If only product id is passed assumed
    that product definition file is in the same folder with .xlsx file extension
    """
    if ".xlsx" not in path:
        path = f"{path}.xlsx"

    return Path(path)


def check_file_exists(product_file_path: Path) -> bool:
    """
    Check that product file exists
    """
    is_exists = os.path.exists(product_file_path)
    if not is_exists:
        raise FileNotExistsError(product_file_path)

    return is_exists


def check_product_definition(
    definition_path: Path, stats: StatsCollector
) -> StatsCollector:
    """
    Parses Product definition file and check consistensy of product definition file
    """
    # check all required columns are defined
    # check parameters and items refer to proper groups
    wb = load_workbook(filename=str(definition_path))

    for sheet_name in REQUIRED_TABS:
        if sheet_name not in wb.sheetnames:
            stats.add_msg(sheet_name, "", "Required tab doesn't exist")

    existing_sheets = set(REQUIRED_TABS).intersection(set(wb.sheetnames))

    for sheet_name in existing_sheets:
        if sheet_name not in REQUIRED_FIELDS_BY_TAB:
            continue

        if sheet_name == TAB_GENERAL:
            check_required_general_fields(
                stats,
                wb.get_sheet_by_name(sheet_name),
                REQUIRED_FIELDS_BY_TAB[sheet_name],
                REQUIRED_FIELDS_WITH_VALUES_BY_TAB[sheet_name],
            )
        else:
            check_required_columns(
                stats,
                wb.get_sheet_by_name(sheet_name),
                REQUIRED_FIELDS_BY_TAB[sheet_name],
            )

    return stats


def check_required_general_fields(
    stats: StatsCollector,
    sheet: Worksheet,
    required_field_names: list[str],
    required_values_field_names: list[str],
) -> StatsCollector:
    """
    Check that required fields and values are presented in General worksheet
    """
    column_values = {v[0].value: v[1].value for v in zip(sheet["A"], sheet["B"])}

    for required_column_name in required_field_names:
        if required_column_name not in column_values:
            stats.add_msg(
                sheet.title,
                "",
                f"Required field {required_column_name} is not provided",
            )

    for required_value_column_name in required_values_field_names:
        if (
            required_value_column_name in column_values
            and not column_values[required_value_column_name]
        ):
            stats.add_msg(
                sheet.title,
                required_value_column_name,
                f"Value is not provided for the required field. "
                f"Current value: {column_values[required_value_column_name]}",
            )

    return stats


def check_required_columns(
    stats: StatsCollector,
    sheet: Worksheet,
    required_field_names: list[str],
) -> StatsCollector:
    """
    Check that required fields and values are presented in tables worksheet
    """
    columns = {v.value for v in sheet["1"]}
    for required_column_name in required_field_names:
        if required_column_name not in columns:
            stats.add_msg(
                sheet.title,
                "",
                f"Required field {required_column_name} is not provided",
            )

    return stats
