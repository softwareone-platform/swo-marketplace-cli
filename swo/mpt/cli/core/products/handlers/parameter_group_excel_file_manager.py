from collections.abc import Generator
from typing import Any

from swo.mpt.cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from swo.mpt.cli.core.products.constants import (
    PARAMETERS_GROUPS_ACTION,
    PARAMETERS_GROUPS_FIELDS,
    PARAMETERS_GROUPS_ID,
    TAB_PARAMETERS_GROUPS,
)
from swo.mpt.cli.core.products.handlers.data_validation import ACTION_DATA_VALIDATION
from swo.mpt.cli.core.products.models import ParameterGroupData


class ParameterGroupExcelFileManager(HorizontalTabFileManager):
    _data_model = ParameterGroupData
    _fields = PARAMETERS_GROUPS_FIELDS
    _id_field = PARAMETERS_GROUPS_ID
    _sheet_name = TAB_PARAMETERS_GROUPS
    _data_validation_map = {PARAMETERS_GROUPS_ACTION: ACTION_DATA_VALIDATION}

    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(self._sheet_name, self._fields)
