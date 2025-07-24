import re
from collections.abc import Generator
from typing import Any

from cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from cli.core.products.constants import ITEMS_ACTION, ITEMS_FIELDS, ITEMS_ID, TAB_ITEMS
from cli.core.products.models import ItemData
from openpyxl.worksheet.datavalidation import DataValidation

ITEMS_ACTION_DATA_VALIDATION = DataValidation(
    type="list", formula1='"-,create,update,review,publish,unpublish"', allow_blank=False
)


class ItemExcelFileManager(HorizontalTabFileManager):
    _data_model = ItemData
    _fields = ITEMS_FIELDS
    _id_field = ITEMS_ID
    _sheet_name = TAB_ITEMS
    _data_validation_map = {ITEMS_ACTION: ITEMS_ACTION_DATA_VALIDATION}

    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_values_for_dynamic_sheet(
            self._sheet_name, ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
        )
