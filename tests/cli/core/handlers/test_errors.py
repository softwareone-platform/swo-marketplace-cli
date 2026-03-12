from cli.core.handlers.errors import ExcelFileHandlerError


def test_excel_file_handler_error_copies_details():
    details = ["Sheet1"]

    details_copy = ExcelFileHandlerError(details=details).details  # act

    assert details_copy is not details
    assert details_copy == ["Sheet1"]
