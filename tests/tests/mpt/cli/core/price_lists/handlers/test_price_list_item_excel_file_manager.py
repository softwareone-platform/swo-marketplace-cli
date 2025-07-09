from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.price_lists.constants import (
    PRICELIST_ITEMS_FIELDS,
    TAB_PRICE_ITEMS,
)
from swo.mpt.cli.core.price_lists.handlers import PriceListItemExcelFileManager


def test_read_data(mocker, item_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    handler = PriceListItemExcelFileManager("fake_file.xlsx")

    result = list(handler._read_data())

    assert result == [mock_data]
    get_data_from_horizontal_sheet_mock.assert_called_once_with(
        TAB_PRICE_ITEMS, PRICELIST_ITEMS_FIELDS
    )
