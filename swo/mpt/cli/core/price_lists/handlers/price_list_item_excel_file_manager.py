from collections.abc import Generator

from openpyxl.worksheet.datavalidation import DataValidation
from swo.mpt.cli.core.handlers.file_manager import ExcelFileManager
from swo.mpt.cli.core.price_lists.constants import (
    ERROR_COLUMN_NAME,
    PRICELIST_ITEMS_ACTION,
    PRICELIST_ITEMS_FIELDS,
    PRICELIST_ITEMS_ID,
    TAB_PRICE_ITEMS,
)
from swo.mpt.cli.core.price_lists.handlers.excel_styles import (
    get_number_format_style,
    price_items_tab_style,
)
from swo.mpt.cli.core.price_lists.models import ItemData


class PriceListItemExcelFileManager(ExcelFileManager):
    _sheet_name = TAB_PRICE_ITEMS
    _data_validation_map = {
        PRICELIST_ITEMS_ACTION: DataValidation(
            type="list", formula1='"-,Updated"', allow_blank=True
        )
    }

    def add(self, items: list[ItemData], precision: int, currency: str) -> None:
        for row, item in enumerate(items, self.file_handler.get_sheet_next_row(self._sheet_name)):
            item_xlsx = item.to_xlsx()
            for col, field in enumerate(PRICELIST_ITEMS_FIELDS, 1):
                value = item_xlsx.get(field, "")
                style = (
                    get_number_format_style(currency, precision)
                    if isinstance(value, float)
                    else None
                )
                self.file_handler.write_cell(
                    self._sheet_name,
                    col=col,
                    row=row,
                    value=value,
                    data_validation=self._data_validation_map.get(field, None),
                    style=style,
                )

        self.file_handler.save()

    def create_tab(self):
        """
        Creates the price list items tab in the Excel file.
        If the file does not exist, it is created.
        """
        if not self.file_handler.exists():
            self.file_handler.create()

        for col, field in enumerate(PRICELIST_ITEMS_FIELDS, 1):
            self.file_handler.write_cell(
                self._sheet_name,
                row=1,
                col=col,
                value=field,
                style=price_items_tab_style,
            )

    def read_items_data(self) -> Generator[ItemData, None, None]:
        """
        Reads all item rows from the price list items sheet and yields them as ItemData objects.

        Yields:
            ItemData: An object containing the data for each item row.
        """
        for item in self.file_handler.get_data_from_horizontal_sheet(
            self._sheet_name, PRICELIST_ITEMS_FIELDS
        ):
            yield ItemData.from_dict(item)

    def write_error(self, error: str, resource_id: str | None = None) -> None:
        """
        Writes an error message to the error column in the price list items sheet.
        If the error column does not exist, it is created.

        Args:
            error: The error message to write.
            resource_id: Resource id related to the error.
        """
        item_row = [
            row
            for row in self.file_handler.get_data_from_horizontal_sheet(
                self._sheet_name, [PRICELIST_ITEMS_ID, ERROR_COLUMN_NAME]
            )
            if row[PRICELIST_ITEMS_ID]["value"] == resource_id
        ][0]
        try:
            coordinate = item_row[ERROR_COLUMN_NAME]["coordinate"]
            column_letter, row_number = self._get_row_and_column_from_coordinate(coordinate)
        except (KeyError, ValueError):
            column_letter = self.file_handler.get_sheet_next_column(self._sheet_name)
            coordinate = next(iter(item_row.values()))["coordinate"]
            _, row_number = self._get_row_and_column_from_coordinate(coordinate)
            self.file_handler.write([{self._sheet_name: {f"{column_letter}1": ERROR_COLUMN_NAME}}])

        self.file_handler.write([{self._sheet_name: {f"{column_letter}{row_number}": error}}])
