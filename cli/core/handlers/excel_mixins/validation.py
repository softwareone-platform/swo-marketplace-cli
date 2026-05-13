from typing import Any

from cli.core.handlers.errors import (
    RequiredFieldsError,
    RequiredFieldValuesError,
    RequiredSheetsError,
)


class ExcelValidationMixin:
    """Provide validation helpers for Excel sheets."""

    _get_fields_from_horizontal_worksheet: Any
    _get_fields_from_vertical_worksheet: Any
    get_data_from_vertical_sheet: Any

    @property
    def sheet_names(self) -> list[str]:
        raise NotImplementedError

    def check_required_sheet(self, required_sheets: tuple[str, ...]) -> None:
        """Checks if specified required sheets exist in the workbook."""
        missed_sheets = [sheet for sheet in required_sheets if sheet not in self.sheet_names]
        if missed_sheets:
            raise RequiredSheetsError(details=missed_sheets)

    def check_required_fields_in_vertical_sheet(
        self, sheet_name: str, required_fields: tuple[str, ...]
    ) -> None:
        """Checks if all required fields are present in a vertical sheet."""
        sheet_fields = self._get_fields_from_vertical_worksheet(sheet_name, 1)
        fields_missed = [field for field in required_fields if field not in sheet_fields]
        if fields_missed:
            raise RequiredFieldsError(details=fields_missed)

    def check_required_field_values_in_vertical_sheet(
        self, sheet_name: str, required_fields: list[str]
    ) -> None:
        """Checks if all required fields have values in a vertical sheet."""
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
        """Checks if all required fields are present in a horizontal sheet."""
        col_fields = self._get_fields_from_horizontal_worksheet(sheet_name, 1)
        missed_fields = [
            required_field for required_field in required_fields if required_field not in col_fields
        ]
        if missed_fields:
            raise RequiredFieldsError(details=missed_fields)
