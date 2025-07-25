from openpyxl.worksheet.datavalidation import DataValidation

ACTION_DATA_VALIDATION = DataValidation(
    type="list", formula1='"-,create,delete,update"', allow_blank=False
)
TERMS_MODEL_DATA_VALIDATION = DataValidation(
    type="list", formula1='"-,one-time,quantity,usage"', allow_blank=False
)
