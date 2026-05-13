from cli.core.handlers.excel_mixins.read import ExcelReadMixin
from cli.core.handlers.excel_mixins.validation import ExcelValidationMixin
from cli.core.handlers.excel_mixins.workbook import ExcelWorkbookMixin
from cli.core.handlers.excel_mixins.worksheet import ExcelWorksheetMixin
from cli.core.handlers.excel_mixins.write import ExcelWriteMixin


class ExcelAccessMixin(ExcelWorkbookMixin, ExcelWorksheetMixin):
    """Group workbook and worksheet access helpers."""


class ExcelSheetMixin(ExcelValidationMixin, ExcelReadMixin, ExcelWriteMixin):
    """Group sheet validation, read, and write helpers."""
