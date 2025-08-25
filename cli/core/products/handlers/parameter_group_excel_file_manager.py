from collections.abc import Generator
from types import MappingProxyType
from typing import Any, override

from cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from cli.core.products.constants import (
    PARAMETERS_GROUPS_ACTION,
    PARAMETERS_GROUPS_FIELDS,
    PARAMETERS_GROUPS_ID,
    TAB_PARAMETERS_GROUPS,
)
from cli.core.products.handlers.data_validation import ACTION_DATA_VALIDATION
from cli.core.products.models import ParameterGroupData


class ParameterGroupExcelFileManager(HorizontalTabFileManager):
    """Excel file manager for parameter group data operations."""

    _data_model = ParameterGroupData
    _fields = PARAMETERS_GROUPS_FIELDS
    _id_field = PARAMETERS_GROUPS_ID
    _sheet_name = TAB_PARAMETERS_GROUPS
    _data_validation_map = MappingProxyType({PARAMETERS_GROUPS_ACTION: ACTION_DATA_VALIDATION})

    @override
    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(self._sheet_name, self._fields)
