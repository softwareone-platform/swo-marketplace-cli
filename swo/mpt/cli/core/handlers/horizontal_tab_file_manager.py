from abc import abstractmethod
from collections.abc import Generator
from typing import Any, Generic, TypeVar

from swo.mpt.cli.core.handlers.constants import ERROR_COLUMN_NAME
from swo.mpt.cli.core.handlers.excel_styles import get_number_format_style, horizontal_tab_style
from swo.mpt.cli.core.handlers.file_manager import ExcelFileManager
from swo.mpt.cli.core.models import BaseDataModel

DataModel = TypeVar("DataModel", bound=BaseDataModel)


class HorizontalTabFileManager(ExcelFileManager, Generic[DataModel]):
    _data_model: type[DataModel]
    _fields: list[str]
    _id_field: str
    _required_tabs: list[str]
    _required_fields_by_tab: dict[str, Any]
    _sheet_name: str

    def add(self, items: list[DataModel], precision: int, currency: str) -> None:
        """
        Add a row for each item to the tab.

        Args:
            items: The items to add.
            precision: The number of decimal places to round to.
            currency: The currency to round to.
        """
        for row, item in enumerate(items, self.file_handler.get_sheet_next_row(self._sheet_name)):
            item_xlsx = item.to_xlsx()
            for col, field in enumerate(self._fields, 1):
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

    def create_tab(self) -> None:
        """
        Creates the tab in the Excel file. If the file does not exist, it is created.
        """
        if not self.file_handler.exists():
            self.file_handler.create()

        for col, field in enumerate(self._fields, 1):
            self.file_handler.write_cell(
                self._sheet_name,
                row=1,
                col=col,
                value=field,
                style=horizontal_tab_style,
            )

    def read_data(self) -> Generator[BaseDataModel, None, None]:
        """
        Reads all item rows from the sheet and yields them as DataModel objects.

        Yields:
            DataModel: An object containing the data for each item row.
        """
        for item in self._read_data():
            yield self._data_model.from_dict(item)

    def write_error(self, error: str, resource_id: str | None = None) -> None:
        """
        Writes an error message to the error column in the sheet.
        If the error column does not exist, it is created.

        Args:
            error: The error message to write.
            resource_id: Resource id related to the error.
        """
        item_row = [
            row
            for row in self.file_handler.get_data_from_horizontal_sheet(
                self._sheet_name, [self._id_field, ERROR_COLUMN_NAME]
            )
            if row[self._id_field]["value"] == resource_id
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

    @abstractmethod
    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        raise NotImplementedError()
