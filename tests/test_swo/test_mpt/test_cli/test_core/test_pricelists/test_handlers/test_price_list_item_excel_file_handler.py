from unittest.mock import call

from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.price_lists.constants import (
    ERROR_COLUMN_NAME,
    PRICELIST_ITEMS_FIELDS,
    PRICELIST_ITEMS_ID,
    TAB_PRICE_ITEMS,
)
from swo.mpt.cli.core.price_lists.handlers.price_list_item_excel_file_handler import (
    PriceListItemExcelFileHandler,
)
from swo.mpt.cli.core.price_lists.models import ItemData


def test_read_items_data(mocker, item_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    item_data_from_dict_mock = mocker.patch.object(
        ItemData, "from_dict", return_value=item_data_from_dict
    )
    handler = PriceListItemExcelFileHandler("fake_file.xlsx")

    result = list(handler.read_items_data())

    assert result == [item_data_from_dict]
    get_data_from_horizontal_sheet_mock.assert_called_once_with(
        TAB_PRICE_ITEMS, PRICELIST_ITEMS_FIELDS
    )
    item_data_from_dict_mock.assert_called_once_with(mock_data)


def test_write_id(mocker):
    write_id_mock = mocker.patch.object(ExcelFileHandler, "write", return_value=None)
    handler = PriceListItemExcelFileHandler("fake_file.xlsx")

    handler.write_id("M12", "new_id")

    write_id_mock.assert_called_once_with([{TAB_PRICE_ITEMS: {"M12": "new_id"}}])


def test_write_error_existing_column(mocker, item_data_from_dict):
    mock_data = {
        "ID": {"value": item_data_from_dict.id, "coordinate": "A2"},
        ERROR_COLUMN_NAME: {"value": "Error", "coordinate": "O2"},
    }
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    write_mock = mocker.patch.object(ExcelFileHandler, "write")
    handler = PriceListItemExcelFileHandler("fake_file.xlsx")

    handler.write_error("fake error message", item_data_from_dict.id)

    get_data_from_horizontal_sheet_mock.assert_called_once_with(
        TAB_PRICE_ITEMS, [PRICELIST_ITEMS_ID, ERROR_COLUMN_NAME]
    )
    write_mock.assert_called_once_with([{TAB_PRICE_ITEMS: {"O2": "fake error message"}}])


def test_write_error_missing_column(mocker, item_data_from_dict):
    mock_data = {"ID": {"value": item_data_from_dict.id, "coordinate": "A19"}}
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    get_sheet_next_column_mock = mocker.patch.object(
        ExcelFileHandler, "get_sheet_next_column", return_value="W"
    )
    write_mock = mocker.patch.object(ExcelFileHandler, "write")
    handler = PriceListItemExcelFileHandler("fake_file.xlsx")

    handler.write_error("fake error message", item_data_from_dict.id)

    get_data_from_horizontal_sheet_mock.assert_called_once_with(
        TAB_PRICE_ITEMS, [PRICELIST_ITEMS_ID, ERROR_COLUMN_NAME]
    )
    get_sheet_next_column_mock.assert_called_once_with(TAB_PRICE_ITEMS)
    write_mock.assert_has_calls(
        [
            call([{TAB_PRICE_ITEMS: {"W1": ERROR_COLUMN_NAME}}]),
            call([{TAB_PRICE_ITEMS: {"W19": "fake error message"}}]),
        ]
    )
