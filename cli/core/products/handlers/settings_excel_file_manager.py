from collections.abc import Generator
from typing import Any, override

from cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from cli.core.products.constants import (
    SETTINGS_ACTION,
    SETTINGS_FIELDS,
    SETTINGS_SETTING,
    TAB_SETTINGS,
)
from cli.core.products.handlers.data_validation import ACTION_DATA_VALIDATION
from cli.core.products.models import SettingsData


class SettingsExcelFileManager(HorizontalTabFileManager):
    """Excel file manager for product settings data operations."""

    _data_model = SettingsData
    _fields = SETTINGS_FIELDS
    _id_field = SETTINGS_SETTING
    _sheet_name = TAB_SETTINGS
    _data_validation_map = {SETTINGS_ACTION: ACTION_DATA_VALIDATION}

    @override
    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(self._sheet_name, self._fields)
