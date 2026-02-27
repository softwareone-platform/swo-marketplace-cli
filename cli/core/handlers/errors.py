class ExcelFileHandlerError(Exception):
    """Base exception class for Excel file handler related errors."""

    _default_message = "Excel file handler error"

    def __init__(self, message: str | None = None, details: list | None = None):
        self.message = self._default_message if message is None else message
        self.details = [] if details is None else details


class RequiredSheetsError(ExcelFileHandlerError):
    """Exception raised when required Excel sheets are missing."""

    _default_message = "Required sheets are missing"


class RequiredFieldsError(ExcelFileHandlerError):
    """Exception raised when required fields are missing from Excel sheets."""

    _default_message = "Required fields are missing"


class RequiredFieldValuesError(ExcelFileHandlerError):
    """Exception raised when required field values are missing from Excel sheets."""

    _default_message = "Required value fields are missing"
