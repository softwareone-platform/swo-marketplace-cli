import re
from collections.abc import Generator
from types import MappingProxyType
from typing import Any, override

from cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from cli.core.products.constants import (
    ITEMS_ACTION,
    ITEMS_FIELDS,
    ITEMS_ID,
    ITEMS_TERMS_MODEL,
    TAB_ITEMS,
)
from cli.core.products.handlers.data_validation import TERMS_MODEL_DATA_VALIDATION
from cli.core.products.models import ItemData
from openpyxl.worksheet.datavalidation import DataValidation

ITEMS_ACTION_DATA_VALIDATION = DataValidation(
    type="list", formula1='"-,create,update,review,publish,unpublish"', allow_blank=False
)


class ItemExcelFileManager(HorizontalTabFileManager):
    """Excel file manager for product item data operations."""

    _data_model = ItemData
    _fields = ITEMS_FIELDS
    _id_field = ITEMS_ID
    _sheet_name = TAB_ITEMS
    _data_validation_map = MappingProxyType({
        ITEMS_ACTION: ITEMS_ACTION_DATA_VALIDATION,
        ITEMS_TERMS_MODEL: TERMS_MODEL_DATA_VALIDATION,
    })

    @override
    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_values_for_dynamic_sheet(
            self._sheet_name, ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
        )
