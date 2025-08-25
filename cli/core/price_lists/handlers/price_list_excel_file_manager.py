from types import MappingProxyType

from cli.core.handlers.vertical_tab_file_manager import VerticalTabFileManager
from cli.core.price_lists.constants import (
    GENERAL_FIELDS,
    GENERAL_PRICELIST_ID,
    REQUIRED_FIELDS_BY_TAB,
    REQUIRED_TABS,
    TAB_GENERAL,
)
from cli.core.price_lists.models import PriceListData


class PriceListExcelFileManager(VerticalTabFileManager):
    """Excel file manager for price list data operations."""

    _data_model = PriceListData
    _fields = GENERAL_FIELDS
    _id_field = GENERAL_PRICELIST_ID
    _required_tabs = REQUIRED_TABS
    _required_fields_by_tab = MappingProxyType(REQUIRED_FIELDS_BY_TAB)
    _sheet_name = TAB_GENERAL
