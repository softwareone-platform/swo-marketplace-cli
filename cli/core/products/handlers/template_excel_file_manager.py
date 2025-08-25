from collections.abc import Generator
from types import MappingProxyType
from typing import Any, override

from cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from cli.core.products.constants import (
    TAB_TEMPLATES,
    TEMPLATES_ACTION,
    TEMPLATES_FIELDS,
    TEMPLATES_ID,
)
from cli.core.products.handlers.data_validation import ACTION_DATA_VALIDATION
from cli.core.products.models import TemplateData


class TemplateExcelFileManager(HorizontalTabFileManager):
    """Excel file manager for template data operations."""

    _data_model = TemplateData
    _fields = TEMPLATES_FIELDS
    _id_field = TEMPLATES_ID
    _sheet_name = TAB_TEMPLATES
    _data_validation_map = MappingProxyType({TEMPLATES_ACTION: ACTION_DATA_VALIDATION})

    @override
    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(self._sheet_name, self._fields)
