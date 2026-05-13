from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


class ExcelWorksheetMixin:
    """Provide worksheet access helpers."""

    _worksheets_cache: dict[str, Worksheet]

    @property
    def workbook(self) -> Workbook:
        raise NotImplementedError

    def _get_fields_from_horizontal_worksheet(self, worksheet_name: str, max_row: int) -> list[str]:
        return list(
            next(self._get_worksheet(worksheet_name).iter_rows(max_row=max_row, values_only=True))  # type: ignore[arg-type]
        )

    def _get_fields_from_vertical_worksheet(self, worksheet_name: str, max_col: int) -> list[str]:
        return list(
            next(self._get_worksheet(worksheet_name).iter_cols(max_col=max_col, values_only=True))  # type: ignore[arg-type]
        )

    def _get_worksheet(self, sheet_name: str) -> Worksheet:
        if self._worksheets_cache.get(sheet_name) is None:
            self._worksheets_cache[sheet_name] = self.workbook[sheet_name]

        return self._worksheets_cache[sheet_name]
