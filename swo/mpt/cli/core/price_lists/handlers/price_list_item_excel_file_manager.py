from collections.abc import Generator
from typing import Any

from openpyxl.worksheet.datavalidation import DataValidation
from swo.mpt.cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from swo.mpt.cli.core.price_lists.constants import (
    PRICELIST_ITEMS_ACTION,
    PRICELIST_ITEMS_FIELDS,
    PRICELIST_ITEMS_ID,
    TAB_PRICE_ITEMS,
)
from swo.mpt.cli.core.price_lists.models import ItemData


class PriceListItemExcelFileManager(HorizontalTabFileManager):
    _data_model = ItemData
    _fields = PRICELIST_ITEMS_FIELDS
    _id_field = PRICELIST_ITEMS_ID
    _sheet_name = TAB_PRICE_ITEMS
    _data_validation_map = {
        PRICELIST_ITEMS_ACTION: DataValidation(
            type="list", formula1='"-,Updated"', allow_blank=True
        )
    }

    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(
            self._sheet_name, PRICELIST_ITEMS_FIELDS
        )
