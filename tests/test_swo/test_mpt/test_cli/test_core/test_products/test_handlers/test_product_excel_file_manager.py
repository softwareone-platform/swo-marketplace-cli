from unittest.mock import call

import pytest
from swo.mpt.cli.core.products.constants import (
    ERROR_COLUMN_NAME,
    GENERAL_FIELDS,
    GENERAL_PRODUCT_ID,
    REQUIRED_FIELDS_BY_TAB,
    REQUIRED_TABS,
    TAB_GENERAL,
)
from swo.mpt.cli.core.products.handlers import ProductExcelFileManager
from swo.mpt.cli.core.products.models import ProductData


@pytest.fixture
def file_manager():
    return ProductExcelFileManager("fake_file_path.xlsx")


def test_add(mocker, file_manager, product_data_from_json):
    write_mock = mocker.patch.object(file_manager.file_handler, "write")

    file_manager.add(product_data_from_json)

    write_mock.assert_called_once()


def test_create_tab(mocker, file_manager):
    exists_mock = mocker.patch.object(file_manager.file_handler, "exists", return_value=True)
    write_cell_mock = mocker.patch.object(file_manager.file_handler, "write_cell")
    merge_cell_mock = mocker.patch.object(file_manager.file_handler, "merge_cells")
    write_mock = mocker.patch.object(file_manager.file_handler, "write")

    file_manager.create_tab()

    exists_mock.assert_called_once()
    write_cell_mock.assert_called_once_with(
        TAB_GENERAL, 1, 1, "General Information", style=mocker.ANY
    )
    merge_cell_mock.assert_called_once_with(TAB_GENERAL, "A1:B1")
    assert write_mock.call_count == len(GENERAL_FIELDS)


def test_check_required_tabs(mocker, file_manager):
    check_required_sheet_mock = mocker.patch.object(
        file_manager.file_handler, "check_required_sheet"
    )

    file_manager.check_required_tabs()

    check_required_sheet_mock.assert_called_once_with(REQUIRED_TABS)


def test_check_required_fields_by_section(mocker, file_manager):
    check_required_fields_in_vertical_mock = mocker.patch.object(
        file_manager.file_handler, "check_required_fields_in_vertical_sheet"
    )
    check_required_field_values_mock = mocker.patch.object(
        file_manager.file_handler, "check_required_field_values_in_vertical_sheet"
    )
    check_required_fields_in_horizontal_mock = mocker.patch.object(
        file_manager.file_handler, "check_required_fields_in_horizontal_sheet"
    )

    file_manager.check_required_fields_by_section()

    check_required_fields_in_vertical_mock.assert_called_once()
    check_required_field_values_mock.assert_called_once()
    check_required_fields_in_horizontal_mock.called_count(len(REQUIRED_FIELDS_BY_TAB) - 1)


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


def test_write_error_existing_column(mocker, file_manager):
    mock_data = {ERROR_COLUMN_NAME: {"value": "Error", "coordinate": "B2"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        file_manager.file_handler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    write_mock = mocker.patch.object(file_manager.file_handler, "write", return_value=None)

    file_manager.write_error("fake error message")

    get_data_from_vertical_sheet_mock.assert_called_once_with(
        TAB_GENERAL, [GENERAL_PRODUCT_ID, ERROR_COLUMN_NAME]
    )
    write_mock.assert_called_with([{TAB_GENERAL: {"B2": "fake error message"}}])


def test_write_error_missing_column(mocker, file_manager):
    mock_data = {"no_data_column": {"value": "fake_value", "coordinate": "AA125"}}
    get_data_from_vertical_sheet_mock = mocker.patch.object(
        file_manager.file_handler, "get_data_from_vertical_sheet", return_value=mock_data
    )
    get_sheet_next_column_mock = mocker.patch.object(
        file_manager.file_handler, "get_sheet_next_column", return_value="AB"
    )
    write_mock = mocker.patch.object(file_manager.file_handler, "write")

    file_manager.write_error("fake error message")

    get_data_from_vertical_sheet_mock.assert_called_once_with(
        TAB_GENERAL, [GENERAL_PRODUCT_ID, ERROR_COLUMN_NAME]
    )
    get_sheet_next_column_mock.assert_called_once_with(TAB_GENERAL)
    write_mock.assert_has_calls(
        [
            call([{TAB_GENERAL: {"AB1": ERROR_COLUMN_NAME}}]),
            call([{TAB_GENERAL: {"AB125": "fake error message"}}]),
        ]
    )
