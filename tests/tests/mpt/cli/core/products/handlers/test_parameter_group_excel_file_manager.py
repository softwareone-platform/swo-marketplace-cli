from cli.core.handlers.excel_file_handler import ExcelFileHandler
from cli.core.products.constants import PARAMETERS_GROUPS_FIELDS, TAB_PARAMETERS_GROUPS
from cli.core.products.handlers import ParameterGroupExcelFileManager
from cli.core.products.models import ParameterGroupData


def test_read_data(mocker, parameter_group_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_horizonal_sheet = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    parameter_group_data_from_dict_mock = mocker.patch.object(
        ParameterGroupData, "from_dict", return_value=parameter_group_data_from_dict
    )
    handler = ParameterGroupExcelFileManager("fake_file.xlsx")

    result = list(handler.read_data())

    assert result == [parameter_group_data_from_dict]
    get_data_from_horizonal_sheet.assert_called_once_with(
        TAB_PARAMETERS_GROUPS, PARAMETERS_GROUPS_FIELDS
    )
    parameter_group_data_from_dict_mock.assert_called_once_with(mock_data)
