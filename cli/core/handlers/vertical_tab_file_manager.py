from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, ClassVar, override

from cli.core.handlers.constants import ERROR_COLUMN_NAME
from cli.core.handlers.excel_styles import general_tab_title_style
from cli.core.handlers.file_manager import ExcelFileManager

if TYPE_CHECKING:
    from cli.core.models import BaseDataModel


class VerticalTabFileManager[DataModel: "BaseDataModel"](ExcelFileManager):
    """File manager for handling vertically-oriented Excel tabs.

    This class manages Excel sheets where data is organized vertically,
    with field names in the first column and corresponding values in
    subsequent columns.
    """

    _data_model: type[DataModel]
    _fields: tuple[str, ...]
    _id_field: str
    _required_tabs: tuple[str, ...]
    _required_fields_by_tab: ClassVar[Mapping[str, Any]]
    _sheet_name: str

    def add(self, data_model: DataModel) -> None:
        """Adds a data model to the Excel sheet.

        Args:
            data_model: The data model to add.

        """
        data_xlsx = data_model.to_xlsx()
        row_values = {}
        for row, field in enumerate(self._fields, 2):
            row_values[f"B{row}"] = data_xlsx.get(field, "")
        self.file_handler.write([{self._sheet_name: row_values}])

    def check_required_tabs(self) -> None:
        """Checks that all required tabs exist in the Excel file."""
        self.file_handler.check_required_sheet(self._required_tabs)

    def check_required_fields_by_section(self) -> None:
        """Checks required fields for each section in the Excel file."""
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

    @override
    def create_tab(self):
        if not self.file_handler.exists():
            self.file_handler.create()

        self.file_handler.write_cell(
            self._sheet_name, 1, 1, "General Information", style=general_tab_title_style
        )
        self.file_handler.merge_cells(self._sheet_name, "A1:B1")

        for row, field in enumerate(self._fields, 2):
            self.file_handler.write([{self._sheet_name: {f"A{row}": field}}])

    def read_data(self) -> DataModel:
        """
        Reads the general information fields from the sheet.

        Returns:
            DataModel: An object containing the information from the sheet.
        """
        row_data = self._read_data(self._fields)
        return self._data_model.from_dict(row_data)

    @override
    def write_error(self, error: str, resource_id: str | None = None) -> None:
        row_data = self._read_data((self._id_field, ERROR_COLUMN_NAME))
        try:
            coordinate = row_data[ERROR_COLUMN_NAME]["coordinate"]
            column_letter, row_number = self._get_row_and_column_from_coordinate(coordinate)
        except KeyError:
            column_letter = self.file_handler.get_sheet_next_column(self._sheet_name)
            coordinate = next(iter(row_data.values()))["coordinate"]
            _, row_number = self._get_row_and_column_from_coordinate(coordinate)
            self.file_handler.write([{self._sheet_name: {f"{column_letter}1": ERROR_COLUMN_NAME}}])

        self.file_handler.write([{self._sheet_name: {f"{column_letter}{row_number}": error}}])

    def _read_data(self, fields: tuple[str, ...]) -> dict[str, Any]:
        return self.file_handler.get_data_from_vertical_sheet(self._sheet_name, fields)
