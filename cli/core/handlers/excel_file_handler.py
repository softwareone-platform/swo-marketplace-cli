import re
from collections.abc import Generator
from pathlib import Path
from re import Pattern
from typing import Any

import openpyxl
from cli.core.handlers import FileHandler
from cli.core.handlers.errors import (
    RequiredFieldsError,
    RequiredFieldValuesError,
    RequiredSheetsError,
)
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.worksheet import Worksheet

type SheetData = dict[str, Any]
type SheetDataGenerator = Generator[SheetData, None, None]
type StyleData = dict[str, dict[str, NamedStyle]]


class ExcelFileHandler(FileHandler):
    """Handler for Excel (.xlsx) file operations."""

    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.__workbook: Workbook | None = None
        self.__worksheets: dict[str, Worksheet] = {}

    @property
    def _workbook(self) -> Workbook:
        if self.__workbook is None:
            self.__workbook = load_workbook(self.file_path)

        return self.__workbook

    @property
    def sheet_names(self) -> list[str]:
        return self._workbook.sheetnames

    @classmethod
    def normalize_file_path(cls, file_path: str) -> Path:
        """Converts a file path string to a Path object with .xlsx extension.

        Args:
            file_path: the file path to normalize.

        Returns:
            A Path object with .xlsx extension.
        """
        return Path(file_path).with_suffix(".xlsx")

    def create(self):
        """Creates a new Excel workbook and saves it to the file_path."""
        wb = openpyxl.Workbook()
        # Change the default sheet name by General
        wb.active.title = "General"

        wb.save(self.file_path)
        wb.close()

    def check_required_sheet(self, required_sheets: tuple[str, ...]) -> None:
        """Checks if specified required sheets exist in the workbook.

        Args:
            required_sheets: List of required sheet names.

        Raises:
            RequiredSheetsError: If any required sheet is missing.
        """
        missed_sheets = [sheet for sheet in required_sheets if sheet not in self.sheet_names]
        if missed_sheets:
            raise RequiredSheetsError(details=missed_sheets)

    # TODO: Extract the common logic with check_horizontal into a separate method.
    def check_required_fields_in_vertical_sheet(
        self, sheet_name: str, required_fields: tuple[str, ...]
    ) -> None:
        """Checks if all required fields are present in a vertical sheet.

        Args:
            sheet_name: The name of the sheet to check.
            required_fields: A list of fields names that must be present in the sheet.

        Raises:
            RequiredFieldsError: If any required fields are missing.
        """
        sheet_fields = self._get_fields_from_vertical_worksheet(sheet_name, 1)
        fields_missed = [field for field in required_fields if field not in sheet_fields]
        if fields_missed:
            raise RequiredFieldsError(details=fields_missed)

    def check_required_field_values_in_vertical_sheet(
        self, sheet_name: str, required_fields: list[str]
    ) -> None:
        """Checks if all required fields have values in a vertical sheet.

        Args:
            sheet_name: The name of the sheet to check.
            required_fields: A list of field names that must have values.

        Raises:
            RequiredFieldValuesError: If any required fields have missing values.
        """
        sheet_data = self.get_data_from_vertical_sheet(sheet_name)
        missed_values = []
        for required_field in required_fields:
            try:
                required_value = sheet_data[required_field]["value"]
            except KeyError:
                continue

            if required_value is None:
                missed_values.append(required_field)

        if missed_values:
            raise RequiredFieldValuesError(details=missed_values)

    def check_required_fields_in_horizontal_sheet(
        self, sheet_name: str, required_fields: list[str]
    ) -> None:
        """Checks if all required fields are present in a horizontal sheet.

        Args:
            sheet_name: The name of the sheet to check.
            required_fields: A list of field names that must be present in the sheet.

        Raises:
            RequiredFieldsError: If any required fields are missing.
        """
        col_fields = self._get_fields_from_horizontal_worksheet(sheet_name, 1)
        missed_fields = [
            required_field for required_field in required_fields if required_field not in col_fields
        ]
        if missed_fields:
            raise RequiredFieldsError(details=missed_fields)

    def get_cell_value_by_coordinate(self, sheet_name: str, coordinate: str) -> str:
        """Retrieves the value of a specific cell in a sheet by its coordinate.

        Args:
            sheet_name: The name of the sheet.
            coordinate: the coordinate of the cell (e.g., "A1", "B2").

        Returns:
            The value of the specified cell
        """
        return self._get_worksheet(sheet_name)[coordinate].value

    def get_data_from_horizontal_sheet(
        self, sheet_name: str, fields: tuple[str, ...] | None = None
    ) -> SheetDataGenerator:
        """Retrieves data from a horizontally oriented sheet.

        Args:
            sheet_name: the name of the sheet.
            fields: a list of column names to extract, or None to extract all columns.

        Yields:
             A dictionary where keys are field names and values are dictionaries containing
                cell values and coordinates.
        """
        sheet = self._get_worksheet(sheet_name)
        header_fields = self._get_fields_from_horizontal_worksheet(sheet_name, 1)
        for row in sheet.iter_rows(min_row=2):
            if all(c.value is None for c in row):
                continue

            yield {
                header_fields[index]: {"value": cell.value, "coordinate": cell.coordinate}
                for index, cell in enumerate(row)
                if fields is None or header_fields[index] in fields
            }

    def get_data_from_vertical_sheet(
        self, sheet_name: str, fields: tuple[str, ...] | None = None
    ) -> SheetData:
        """Extracts data from a vertical sheet where the first column contains field names.

        Args:
            sheet_name: The name of the sheet to extract data from.
            fields: A list of field names to extract, or None to include all fields.

        Returns:
            A dictionary where keys are field names and values are dictionaries containing
                cell values and coordinates.
        """
        sheet = self._get_worksheet(sheet_name)
        sheet_iter = sheet.iter_rows(min_row=2)
        return {
            str(row[0].value): {"value": row[1].value, "coordinate": row[1].coordinate}
            for row in sheet_iter
            if fields is None or row[0].value in fields
        }

    def get_sheet_next_column(self, sheet_name: str) -> str:
        """Get the next available column letter in the specified sheet.

        Args:
            sheet_name: The name of the sheet.

        Returns:
            The next available column letter as a string.

        """
        return get_column_letter(self._get_worksheet(sheet_name).max_column + 1)

    def get_sheet_next_row(self, sheet_name: str) -> int:
        """Get the next available row number in the specified sheet.

        Args:
            sheet_name: The name of the sheet.

        Returns:
            The next available row number (1-based index).

        """
        return self._get_worksheet(sheet_name).max_row + 1

    def get_values_for_dynamic_sheet(
        self, sheet_name: str, fields: tuple[str, ...], patterns: list[Pattern[str]]
    ) -> SheetDataGenerator:
        """Extracts data from a sheet with a dynamic column structure.

        Args:
            sheet_name: The name of the sheet to extract data from.
            fields: A list of field names to match in the columns
            patterns: A list of regex patterns to match column names

        Yields:
            Tuples containing cell coordinate, column name, and cell value
        """
        ws = self._get_worksheet(sheet_name)
        column_map = {}
        for index, column in enumerate(ws["1"]):
            if column.value and (
                column.value in fields or any(re.match(p, column.value) for p in patterns)
            ):
                column_map[index] = column.value

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            if all(c.value is None for c in row):
                continue

            yield {
                column_name: {
                    "value": row[index].value,
                    "coordinate": f"{row[index].column_letter}{row[index].row}",  # type: ignore[union-attr]
                }
                for index, column_name in column_map.items()
            }

    def merge_cells(self, sheet_name: str, range_string: str) -> None:
        """Merges a range of cells in the specified sheet.

        Args:
            sheet_name: The name of the sheet.
            range_string: The cell range to merge (e.g., "A1:B2").

        """
        self._workbook[sheet_name].merge_cells(range_string)

    def read(self) -> list[Any]:
        """
        Reads data from all sheets in the workbook.

        Returns: A list
        """
        # TBD
        return []

    def save(self) -> None:
        """Saves the current workbook to the file path and cleans worksheet cache."""
        self._workbook.save(self.file_path)
        self._clean_worksheets()

    def write(self, sheet_rows: list[SheetData]) -> None:
        """
        Writes data to the Excel workbook.

        Args:
            sheet_rows: A list of dictionaries where each dictionary represents a sheet with
                cell coordinates as keys and values to be written
        """
        for sheet in sheet_rows:
            for sheet_name, cells in sheet.items():
                try:
                    worksheet = self._get_worksheet(sheet_name)
                except KeyError:
                    worksheet = self._workbook.create_sheet(title=sheet_name)

                for coordinate, cell_value in cells.items():
                    worksheet[coordinate] = cell_value

        self.save()

    def write_cell(
        self,
        sheet_name: str,
        col: int,
        row: int,
        cell_value: str,
        data_validation: DataValidation | None = None,
        style: NamedStyle | None = None,
    ) -> None:
        """Writes a value to a cell, applying style and data validation if provided.

        Args:
            sheet_name: The name of the sheet.
            col: The column number (1-based).
            row: The row number (1-based).
            cell_value: The value to write to the cell.
            data_validation: Optional data validation to apply.
            style: Optional cell style to apply.

        """
        try:
            sheet = self._get_worksheet(sheet_name)
        except KeyError:
            sheet = self._workbook.create_sheet(title=sheet_name)

        coordinate = f"{get_column_letter(col)}{row}"
        if style is not None:
            sheet[coordinate].style = style

        if data_validation is not None:
            if data_validation not in list(sheet.data_validations):
                sheet.add_data_validation(data_validation)
            data_validation.add(sheet[coordinate])

        sheet[coordinate] = cell_value

    def _clean_worksheets(self, sheet_name: str | None = None) -> None:
        if sheet_name is not None:
            self.__worksheets.pop(sheet_name, None)
        else:
            self.__worksheets = {}

    def _get_fields_from_horizontal_worksheet(self, worksheet_name: str, max_row: int) -> list[str]:
        return list(
            next(self._get_worksheet(worksheet_name).iter_rows(max_row=max_row, values_only=True))  # type: ignore[arg-type]
        )

    def _get_fields_from_vertical_worksheet(self, worksheet_name: str, max_col: int) -> list[str]:
        return list(
            next(self._get_worksheet(worksheet_name).iter_cols(max_col=max_col, values_only=True))  # type: ignore[arg-type]
        )

    def _get_worksheet(self, sheet_name: str) -> Worksheet:
        if self.__worksheets.get(sheet_name) is None:
            self.__worksheets[sheet_name] = self._workbook[sheet_name]

        return self.__worksheets[sheet_name]
