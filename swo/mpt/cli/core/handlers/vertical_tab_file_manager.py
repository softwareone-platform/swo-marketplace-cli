from typing import Any, Generic, TypeVar

from swo.mpt.cli.core.handlers.constants import ERROR_COLUMN_NAME
from swo.mpt.cli.core.handlers.excel_styles import general_tab_title_style
from swo.mpt.cli.core.handlers.file_manager import ExcelFileManager
from swo.mpt.cli.core.models import BaseDataModel

DataModel = TypeVar("DataModel", bound=BaseDataModel)


class VerticalTabFileManager(ExcelFileManager, Generic[DataModel]):
    _data_model: type[DataModel]
    _fields: list[str]
    _id_field: str
    _required_tabs: list[str]
    _required_fields_by_tab: dict[str, Any]
    _sheet_name: str

    def add(self, data_model: BaseDataModel) -> None:
        data_xlsx = data_model.to_xlsx()
        data = {f"B{row}": data_xlsx.get(field, "") for row, field in enumerate(self._fields, 2)}
        self.file_handler.write([{self._sheet_name: data}])

    def check_required_tabs(self) -> None:
        self.file_handler.check_required_sheet(self._required_tabs)

    def check_required_fields_by_section(self) -> None:
        for section, required_fields in self._required_fields_by_tab.items():
            if section == self._sheet_name:
                self.file_handler.check_required_fields_in_vertical_sheet(section, required_fields)
                self.file_handler.check_required_field_values_in_vertical_sheet(
                    section, required_fields
                )
            else:
                self.file_handler.check_required_fields_in_horizontal_sheet(
                    section, required_fields
                )

    def create_tab(self):
        """
        Creates the general information tab in the Excel file.
        If the file does not exist, it is created.
        """
        if not self.file_handler.exists():
            self.file_handler.create()

        self.file_handler.write_cell(
            self._sheet_name, 1, 1, "General Information", style=general_tab_title_style
        )
        self.file_handler.merge_cells(self._sheet_name, "A1:B1")

        for row, field in enumerate(self._fields, 2):
            self.file_handler.write([{self._sheet_name: {f"A{row}": field}}])

    def read_data(self) -> BaseDataModel:
        """
        Reads the general information fields from the sheet.

        Returns:
            DataModel: An object containing the information from the sheet.
        """
        data = self._read_data(self._fields)
        return self._data_model.from_dict(data)

    def write_error(self, error: str, resource_id: str | None = None) -> None:
        """
        Writes an error message to the error column in the sheet.
        If the error column does not exist, it is created.

        Args:
            error: The error message to write.
            resource_id: Resource id related to the error.
        """
        data = self._read_data([self._id_field, ERROR_COLUMN_NAME])
        try:
            coordinate = data[ERROR_COLUMN_NAME]["coordinate"]
            column_letter, row_number = self._get_row_and_column_from_coordinate(coordinate)
        except KeyError:
            column_letter = self.file_handler.get_sheet_next_column(self._sheet_name)
            coordinate = next(iter(data.values()))["coordinate"]
            _, row_number = self._get_row_and_column_from_coordinate(coordinate)
            self.file_handler.write([{self._sheet_name: {f"{column_letter}1": ERROR_COLUMN_NAME}}])

        self.file_handler.write([{self._sheet_name: {f"{column_letter}{row_number}": error}}])

    def _read_data(self, fields: list[str]) -> dict[str, Any]:
        return self.file_handler.get_data_from_vertical_sheet(self._sheet_name, fields)
