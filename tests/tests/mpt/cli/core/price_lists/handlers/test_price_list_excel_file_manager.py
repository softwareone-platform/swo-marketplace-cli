from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.price_lists.constants import (
    GENERAL_FIELDS,
    TAB_GENERAL,
)
from swo.mpt.cli.core.price_lists.handlers import PriceListExcelFileManager
from swo.mpt.cli.core.price_lists.models import PriceListData


def test_read_data(mocker, price_list_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    price_list_from_dict_mock = mocker.patch.object(
        PriceListData, "from_dict", return_value=price_list_data_from_dict
    )
    handler = PriceListExcelFileManager("fake_file.xlsx")

    result = handler.read_data()

    assert result == price_list_data_from_dict
    get_data_from_vertical_sheet_mock.assert_called_once_with(TAB_GENERAL, GENERAL_FIELDS)
    price_list_from_dict_mock.assert_called_once_with(mock_data)
