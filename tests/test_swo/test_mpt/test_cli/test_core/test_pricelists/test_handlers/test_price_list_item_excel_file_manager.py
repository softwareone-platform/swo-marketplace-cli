from unittest.mock import call

from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.price_lists.constants import (
    ERROR_COLUMN_NAME,
    PRICELIST_ITEMS_FIELDS,
    PRICELIST_ITEMS_ID,
    TAB_PRICE_ITEMS,
)
from swo.mpt.cli.core.price_lists.handlers.price_list_item_excel_file_manager import (
    PriceListItemExcelFileManager,
)
from swo.mpt.cli.core.price_lists.models import ItemData


def test_add(mocker, item_data_from_json):
    write_cell_mock = mocker.patch.object(ExcelFileHandler, "write_cell")
    get_sheet_next_row_mock = mocker.patch.object(
        ExcelFileHandler, "get_sheet_next_row", return_value=2
    )
    save_mock = mocker.patch.object(ExcelFileHandler, "save")
    handler = PriceListItemExcelFileManager("fake_file.xlsx")

    handler.add([item_data_from_json], precision=2, currency="USD")

    assert write_cell_mock.call_count == len(PRICELIST_ITEMS_FIELDS)
    save_mock.assert_called_once()
    get_sheet_next_row_mock.assert_called_once()


def test_create_tab(mocker):
    exists_mock = mocker.patch.object(ExcelFileHandler, "exists", return_value=False)
    create_mock = mocker.patch.object(ExcelFileHandler, "create")
    write_cell_mock = mocker.patch.object(ExcelFileHandler, "write_cell")
    handler = PriceListItemExcelFileManager("fake_file.xlsx")

    handler.create_tab()

    exists_mock.assert_called_once()
    create_mock.assert_called_once()
    assert write_cell_mock.call_count == len(PRICELIST_ITEMS_FIELDS)


def test_read_items_data(mocker, item_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    item_data_from_dict_mock = mocker.patch.object(
        ItemData, "from_dict", return_value=item_data_from_dict
    )
    handler = PriceListItemExcelFileManager("fake_file.xlsx")

    result = list(handler.read_items_data())

    assert result == [item_data_from_dict]
    get_data_from_horizontal_sheet_mock.assert_called_once_with(
        TAB_PRICE_ITEMS, PRICELIST_ITEMS_FIELDS
    )
    item_data_from_dict_mock.assert_called_once_with(mock_data)


def test_write_error_existing_column(mocker, item_data_from_dict):
    mock_data = {
        "ID": {"value": item_data_from_dict.id, "coordinate": "A2"},
        ERROR_COLUMN_NAME: {"value": "Error", "coordinate": "O2"},
    }
    get_data_from_horizontal_sheet_mock = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    write_mock = mocker.patch.object(ExcelFileHandler, "write")
    handler = PriceListItemExcelFileManager("fake_file.xlsx")

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
    handler = PriceListItemExcelFileManager("fake_file.xlsx")

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
