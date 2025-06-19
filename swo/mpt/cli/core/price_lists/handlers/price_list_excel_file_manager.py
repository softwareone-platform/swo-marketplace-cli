from typing import Any

from swo.mpt.cli.core.handlers.excel_styles import general_tab_title_style
from swo.mpt.cli.core.handlers.file_manager import ExcelFileManager
from swo.mpt.cli.core.price_lists.constants import (
    ERROR_COLUMN_NAME,
    GENERAL_FIELDS,
    GENERAL_PRICELIST_ID,
    TAB_GENERAL,
)
from swo.mpt.cli.core.price_lists.models import PriceListData


class PriceListExcelFileManager(ExcelFileManager):
    _sheet_name = TAB_GENERAL

    def add(self, price_list: PriceListData) -> None:
        price_list_xlsx = price_list.to_xlsx()
        data = {
            f"B{row}": price_list_xlsx.get(field, "") for row, field in enumerate(GENERAL_FIELDS, 2)
        }
        self.file_handler.write([{self._sheet_name: data}])

    def create_tab(self):
        """
        Creates the general information tab in the price list Excel file.
        If the file does not exist, it is created.
        """
        if not self.file_handler.exists():
            self.file_handler.create()

        self.file_handler.write_cell(
            self._sheet_name, 1, 1, "General Information", style=general_tab_title_style
        )
        self.file_handler.merge_cells(self._sheet_name, "A1:B1")

        for row, field in enumerate(GENERAL_FIELDS, 2):
            self.file_handler.write([{self._sheet_name: {f"A{row}": field}}])

    def read_general_data(self) -> PriceListData:
        """
        Reads the general information fields from the price list sheet.

        Returns:
            PriceListData: An object containing the general information from the sheet.
        """
        data = self._read_general_data(GENERAL_FIELDS)
        return PriceListData.from_dict(data)

    def write_error(self, error: str, resource_id: str | None = None) -> None:
        """
        Writes an error message to the error column in the price list sheet.
        If the error column does not exist, it is created.

        Args:
            error: The error message to write.
            resource_id: Resource id related to the error.
        """
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
