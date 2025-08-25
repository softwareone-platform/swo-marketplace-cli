from collections.abc import Generator
from types import MappingProxyType
from typing import Any, override

from cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from cli.core.products.constants import (
    ITEMS_ACTION,
    ITEMS_GROUPS_FIELDS,
    ITEMS_GROUPS_ID,
    TAB_ITEMS_GROUPS,
)
from cli.core.products.handlers.data_validation import ACTION_DATA_VALIDATION
from cli.core.products.models import ItemGroupData


class ItemGroupExcelFileManager(HorizontalTabFileManager):
    """Excel file manager for item group data operations."""

    _data_model = ItemGroupData
    _fields = ITEMS_GROUPS_FIELDS
    _id_field = ITEMS_GROUPS_ID
    _sheet_name = TAB_ITEMS_GROUPS
    _data_validation_map = MappingProxyType({ITEMS_ACTION: ACTION_DATA_VALIDATION})

    @override
    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(self._sheet_name, self._fields)
