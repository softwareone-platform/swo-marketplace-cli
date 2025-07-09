import pytest
from swo.mpt.cli.core.products.constants import (
    GENERAL_FIELDS,
    TAB_GENERAL,
)
from swo.mpt.cli.core.products.handlers import ProductExcelFileManager
from swo.mpt.cli.core.products.models import ProductData


@pytest.fixture
def file_manager():
    return ProductExcelFileManager("fake_file_path.xlsx")


def test_read_data(mocker, file_manager, product_data_from_dict):
    mock_data = {"fake_field1": {"field"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        file_manager.file_handler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    product_from_dict_mock = mocker.patch.object(
        ProductData, "from_dict", return_value=product_data_from_dict
    )

    result = file_manager.read_data()

    assert result == product_data_from_dict
    get_data_from_vertical_sheet_mock.assert_called_once_with(TAB_GENERAL, GENERAL_FIELDS)
    product_from_dict_mock.assert_called_once_with(mock_data)
