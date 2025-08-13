import pytest
from cli.core.handlers.excel_file_handler import ExcelFileHandler
from cli.core.handlers.file_manager import ExcelFileManager


class FakeExcelFileManager(ExcelFileManager):
    _sheet_name = "fake_sheet_name"

    def create_tab(self):
        pass

    def write_error(self, error, resource_id=None):
        pass


def test_get_row_and_column_from_coordinate_valid():
    col, row = FakeExcelFileManager._get_row_and_column_from_coordinate("B12")  # noqa: SLF001

    assert col == "B"
    assert row == 12


def test_get_row_and_column_from_coordinate_invalid():
    with pytest.raises(ValueError):
        FakeExcelFileManager._get_row_and_column_from_coordinate("")  # noqa: SLF001


def test_write_ids(mocker):
    file_handler_spy = mocker.patch.object(ExcelFileHandler, "write")
    file_manager = FakeExcelFileManager("/tmp/fake.xlsx")  # noqa: S108

    file_manager.write_ids({"A1": "12345"})

    file_handler_spy.assert_called_once_with([{file_manager._sheet_name: {"A1": "12345"}}])  # noqa: SLF001
