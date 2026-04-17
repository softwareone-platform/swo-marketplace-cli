from dataclasses import dataclass
from pathlib import Path

from cli.core.handlers import FileHandler
from cli.core.handlers.excel_file_handler_mixins import ExcelAccessMixin, ExcelSheetMixin
from openpyxl.reader.excel import load_workbook  # noqa: F401
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


@dataclass(frozen=True)
class CellPosition:
    """Represents a worksheet cell position."""

    col: int
    row: int


class ExcelFileHandler(ExcelAccessMixin, ExcelSheetMixin, FileHandler):
    """Handler for Excel (.xlsx) file operations."""

    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self._workbook_cache: Workbook | None = None
        self._worksheets_cache: dict[str, Worksheet] = {}
