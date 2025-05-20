class ExcelFileHandlerError(Exception):
    _default_message = "Excel file handler error"

    def __init__(self, message: None | str = None, details: None | list = None):
        self.message = message if message is not None else self._default_message
        self.details = details if details is not None else []


class RequiredSheetsError(ExcelFileHandlerError):
    _default_message = "Required sheets are missing"


class RequiredFieldsError(ExcelFileHandlerError):
    _default_message = "Required fields are missing"


class RequiredFieldValuesError(ExcelFileHandlerError):
    _default_message = "Required value fields are missing"
