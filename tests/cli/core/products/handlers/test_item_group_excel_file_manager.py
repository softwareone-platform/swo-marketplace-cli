from cli.core.handlers.excel_file_handler import ExcelFileHandler
from cli.core.products.constants import ITEMS_GROUPS_FIELDS, TAB_ITEMS_GROUPS
from cli.core.products.handlers import ItemGroupExcelFileManager
from cli.core.products.models import ItemGroupData


def test_read_data(mocker, item_group_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_horizonal_sheet = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    item_group_data_from_dict_mock = mocker.patch.object(
        ItemGroupData, "from_dict", return_value=item_group_data_from_dict
    )
    excel_manager = ItemGroupExcelFileManager("fake_file.xlsx")

    result = list(excel_manager.read_data())

    assert result == [item_group_data_from_dict]
    get_data_from_horizonal_sheet.assert_called_once_with(TAB_ITEMS_GROUPS, ITEMS_GROUPS_FIELDS)
    item_group_data_from_dict_mock.assert_called_once_with(mock_data)
