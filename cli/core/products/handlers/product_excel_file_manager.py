from types import MappingProxyType

from cli.core.handlers.vertical_tab_file_manager import VerticalTabFileManager
from cli.core.products.constants import (
    GENERAL_FIELDS,
    GENERAL_PRODUCT_ID,
    REQUIRED_FIELDS_BY_TAB,
    REQUIRED_TABS,
    TAB_GENERAL,
)
from cli.core.products.models import ProductData


class ProductExcelFileManager(VerticalTabFileManager):
    """Excel file manager for product data operations."""

    _data_model = ProductData
    _fields = GENERAL_FIELDS
    _id_field = GENERAL_PRODUCT_ID
    _required_tabs = REQUIRED_TABS
    _required_fields_by_tab = MappingProxyType(REQUIRED_FIELDS_BY_TAB)
    _sheet_name = TAB_GENERAL
