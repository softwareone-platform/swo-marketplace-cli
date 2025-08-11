class ExcelFileHandlerError(Exception):
    """Base exception class for Excel file handler related errors."""

    _default_message = "Excel file handler error"

    def __init__(self, message: None | str = None, details: None | list = None):
        self.message = message if message is not None else self._default_message
        self.details = details if details is not None else []


class RequiredSheetsError(ExcelFileHandlerError):
    """Exception raised when required Excel sheets are missing."""

    _default_message = "Required sheets are missing"


class RequiredFieldsError(ExcelFileHandlerError):
    """Exception raised when required fields are missing from Excel sheets."""

    _default_message = "Required fields are missing"


class RequiredFieldValuesError(ExcelFileHandlerError):
    """Exception raised when required field values are missing from Excel sheets."""

    _default_message = "Required value fields are missing"
