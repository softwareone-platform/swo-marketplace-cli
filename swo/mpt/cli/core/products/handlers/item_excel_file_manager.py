import re
from collections.abc import Generator
from typing import Any

from swo.mpt.cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from swo.mpt.cli.core.products.constants import ITEMS_FIELDS, ITEMS_ID, TAB_ITEMS
from swo.mpt.cli.core.products.models import ItemData


class ItemExcelFileManager(HorizontalTabFileManager):
    _data_model = ItemData
    _fields = ITEMS_FIELDS
    _id_field = ITEMS_ID
    _sheet_name = TAB_ITEMS

    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_values_for_dynamic_sheet(
            self._sheet_name, ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
        )
