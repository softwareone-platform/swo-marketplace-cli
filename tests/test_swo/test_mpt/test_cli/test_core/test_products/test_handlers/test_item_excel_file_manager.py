import re

from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.products.constants import (
    ITEMS_FIELDS,
    TAB_ITEMS,
)
from swo.mpt.cli.core.products.handlers import ItemExcelFileManager
from swo.mpt.cli.core.products.models import ItemData


def test_read_data(mocker, item_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_values_for_dynamic_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_values_for_dynamic_sheet", return_value=iter([mock_data])
    )
    item_data_from_dict_mock = mocker.patch.object(
        ItemData, "from_dict", return_value=item_data_from_dict
    )
    handler = ItemExcelFileManager("fake_file.xlsx")

    result = list(handler.read_data())

    assert result == [item_data_from_dict]
    get_values_for_dynamic_sheet_mock.assert_called_once_with(
        TAB_ITEMS, ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
    )
    item_data_from_dict_mock.assert_called_once_with(mock_data)
