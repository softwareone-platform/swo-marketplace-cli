import re
from collections.abc import Generator
from pathlib import Path
from typing import Any

from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.pricelists.constants import (
    ERROR_COLUMN_NAME,
    GENERAL_FIELDS,
    GENERAL_PRICELIST_ID,
    PRICELIST_ITEMS_FIELDS,
    TAB_GENERAL,
    TAB_PRICE_ITEMS,
)
from swo.mpt.cli.core.pricelists.models import ItemData, PriceListData


class PriceListExcelFileHandler:
    _sheet_name = TAB_GENERAL

    def __init__(self, file_path: str):
        self.file_handler = ExcelFileHandler(Path(file_path))

    def read_general_data(self) -> PriceListData:
        data = self._read_general_data(GENERAL_FIELDS)
        return PriceListData.from_dict(data)

    def read_items_data(self) -> Generator[ItemData, None, None]:
        for item in self.file_handler.get_data_from_horizontal_sheet(
            TAB_PRICE_ITEMS, PRICELIST_ITEMS_FIELDS
        ):
            yield ItemData.from_dict(item)

    def write_id(self, coordinate: str, new_id: str) -> None:
        self.file_handler.write([{self._sheet_name: {coordinate: new_id}}])

    def write_error(self, error: str) -> None:
        data = self._read_general_data([GENERAL_PRICELIST_ID, ERROR_COLUMN_NAME])
        try:
            coordinate = data[ERROR_COLUMN_NAME]["coordinate"]
            column_letter, row_number = self._get_row_and_column_from_coordinate(coordinate)
        except KeyError:
            column_letter = self.file_handler.get_sheet_next_column(self._sheet_name)
            coordinate = next(iter(data.values()))["coordinate"]
            _, row_number = self._get_row_and_column_from_coordinate(coordinate)
            self.file_handler.write([{self._sheet_name: {f"{column_letter}1": ERROR_COLUMN_NAME}}])

        self.file_handler.write([{self._sheet_name: {f"{column_letter}{row_number}": error}}])

    def _read_general_data(self, fields: list[str]) -> dict[str, Any]:
        return self.file_handler.get_data_from_vertical_sheet(self._sheet_name, fields)

    def _get_row_and_column_from_coordinate(self, coordinate: str) -> tuple[str, int]:
        match = re.match(r"([A-Z]+)(\d+)", coordinate)
        if not match:
            raise ValueError(f"Invalid coordinate format: {coordinate}")
        column_letter, row_number = match.groups()
        return column_letter, int(row_number)
