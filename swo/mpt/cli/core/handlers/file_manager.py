import re
from abc import ABC, abstractmethod
from pathlib import Path

from openpyxl.worksheet.datavalidation import DataValidation
from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler


class ExcelFileManager(ABC):
    _sheet_name: str
    _data_validation_map: dict[str, DataValidation] = {}

    def __init__(self, file_path: str):
        self.file_handler = ExcelFileHandler(Path(file_path))

    @abstractmethod
    def create_tab(self) -> None:
        """
        Creates a new tab (worksheet) in the Excel file.
        """
        raise NotImplementedError

    @abstractmethod
    def write_error(self, error: str, resource_id: str | None = None) -> None:
        """
        Writes an error message to the Excel file.

        Args:
            error: The error message to write.
            resource_id: Resource id related to the error.
        """
        raise NotImplementedError

    def write_id(self, coordinate: str, new_id: str) -> None:
        """
        Writes a new ID value to the specified cell coordinate in the managed sheet.

        Args:
            coordinate: The cell coordinate (e.g., 'A1') to write the ID to.
            new_id: The ID value to write.
        """
        self.file_handler.write([{self._sheet_name: {coordinate: new_id}}])

    @staticmethod
    def _get_row_and_column_from_coordinate(coordinate: str) -> tuple[str, int]:
        """
        Parses an Excel cell coordinate and returns its column letter and row number.

        Args:
            coordinate: The cell coordinate (e.g., 'A1').

        Returns:
            A tuple containing the column letter and row number.

        Raises:
            ValueError: If the coordinate format is invalid.
        """
        match = re.match(r"([A-Z]+)(\d+)", coordinate)
        if not match:
            raise ValueError(f"Invalid coordinate format: {coordinate}")

        column_letter, row_number = match.groups()
        return column_letter, int(row_number)
