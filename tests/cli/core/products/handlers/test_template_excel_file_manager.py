from cli.core.handlers.excel_file_handler import ExcelFileHandler
from cli.core.products.constants import TAB_TEMPLATES, TEMPLATES_FIELDS
from cli.core.products.handlers import TemplateExcelFileManager
from cli.core.products.models import TemplateData


def test_read_data(mocker, template_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_horizonal_sheet = mocker.patch.object(
        ExcelFileHandler, "get_data_from_horizontal_sheet", return_value=iter([mock_data])
    )
    template_data_from_dict_mock = mocker.patch.object(
        TemplateData, "from_dict", return_value=template_data_from_dict
    )
    handler = TemplateExcelFileManager("fake_file.xlsx")

    result = list(handler.read_data())

    assert result == [template_data_from_dict]
    get_data_from_horizonal_sheet.assert_called_once_with(TAB_TEMPLATES, TEMPLATES_FIELDS)
    template_data_from_dict_mock.assert_called_once_with(mock_data)
