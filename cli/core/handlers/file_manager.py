import re
from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path
from typing import Any, ClassVar

from cli.core.handlers.excel_file_handler import ExcelFileHandler
from openpyxl.worksheet.datavalidation import DataValidation


class ExcelFileManager(ABC):
    """Abstract base class for managing Excel file operations.

    This class provides common functionality for Excel file managers,
    including tab management, error handling, and data writing operations.
    """

    _sheet_name: str
    _data_validation_map: ClassVar[Mapping[str, DataValidation]] = {}

    @property
    def tab_name(self) -> str:
        return self._sheet_name

    def __init__(self, file_path: str):
        self.file_handler = ExcelFileHandler(Path(file_path))

    @abstractmethod
    def create_tab(self) -> None:
        """Creates a new tab (worksheet) in the Excel file."""
        raise NotImplementedError

    @abstractmethod
    def write_error(self, error: str, resource_id: str | None = None) -> None:
        """Writes an error message to the Excel file.

        Args:
            error: The error message to write.
            resource_id: Resource id related to the error.
        """
        raise NotImplementedError

    def write_ids(self, id_map: dict[str, Any]) -> None:
        """Writes the IDs into the managed sheet.

        Args:
            id_map: A dict where each key is a cell coordinate (e.g., 'A1') and each value is
            the corresponding ID.
        """
        self.file_handler.write([{self._sheet_name: id_map}])

    @staticmethod
    def _get_row_and_column_from_coordinate(coordinate: str) -> tuple[str, int]:
        """Parses an Excel cell coordinate and returns its column letter and row number.

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
