import pytest
from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.handlers.file_manager import ExcelFileManager


class FakeExcelFileManager(ExcelFileManager):
    _sheet_name = "fake_sheet_name"

    def create_tab(self):
        pass

    def write_error(self, error, resource_id=None):
        pass


def test_get_row_and_column_from_coordinate_valid():
    col, row = FakeExcelFileManager._get_row_and_column_from_coordinate("B12")

    assert col == "B"
    assert row == 12


def test_get_row_and_column_from_coordinate_invalid():
    with pytest.raises(ValueError):
        FakeExcelFileManager._get_row_and_column_from_coordinate("")


def test_write_id(mocker):
    file_handler_spy = mocker.patch.object(ExcelFileHandler, "write")
    file_manager = FakeExcelFileManager("/tmp/fake.xlsx")

    file_manager.write_id("A1", "12345")

    file_handler_spy.assert_called_once_with([{file_manager._sheet_name: {"A1": "12345"}}])
