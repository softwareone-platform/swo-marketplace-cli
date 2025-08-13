from abc import ABC
from collections.abc import Generator
from types import MappingProxyType
from typing import Any, override

from cli.core.models import BaseDataModel

from cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from cli.core.products.constants import (
    PARAMETERS_ACTION,
    PARAMETERS_FIELDS,
    PARAMETERS_ID,
    TAB_AGREEMENT_PARAMETERS,
    TAB_ITEM_PARAMETERS,
    TAB_REQUEST_PARAMETERS,
    TAB_SUBSCRIPTION_PARAMETERS,
)
from cli.core.products.handlers.data_validation import ACTION_DATA_VALIDATION
from cli.core.products.models import (
    AgreementParametersData,
    ItemParametersData,
    RequestParametersData,
    SubscriptionParametersData,
)


class ParametersExcelFileManager[DataModel: BaseDataModel](HorizontalTabFileManager, ABC):
    """Excel file manager for parameter data operations."""

    _data_model: type[DataModel]
    _sheet_name: str
    _fields = PARAMETERS_FIELDS
    _id_field = PARAMETERS_ID
    _data_validation_map = MappingProxyType({PARAMETERS_ACTION: ACTION_DATA_VALIDATION})

    @override
    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(self._sheet_name, self._fields)


class AgreementParametersExcelFileManager(ParametersExcelFileManager):
    """Excel file manager for agreement parameter data operations."""

    _data_model = AgreementParametersData
    _sheet_name = TAB_AGREEMENT_PARAMETERS


class ItemParametersExcelFileManager(ParametersExcelFileManager):
    """Excel file manager for item parameter data operations."""

    _data_model = ItemParametersData
    _sheet_name = TAB_ITEM_PARAMETERS


class RequestParametersExcelFileManager(ParametersExcelFileManager):
    """Excel file manager for request parameter data operations."""

    _data_model = RequestParametersData
    _sheet_name = TAB_REQUEST_PARAMETERS


class SubscriptionParametersExcelFileManager(ParametersExcelFileManager):
    """Excel file manager for subscription parameter data operations."""

    _data_model = SubscriptionParametersData
    _sheet_name = TAB_SUBSCRIPTION_PARAMETERS
