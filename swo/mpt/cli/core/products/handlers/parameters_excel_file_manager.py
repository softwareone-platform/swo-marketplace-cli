from abc import ABC
from collections.abc import Generator
from typing import Any, Generic, TypeVar

from swo.mpt.cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products.constants import (
    PARAMETERS_FIELDS,
    PARAMETERS_ID,
    TAB_AGREEMENT_PARAMETERS,
    TAB_ITEM_PARAMETERS,
    TAB_REQUEST_PARAMETERS,
    TAB_SUBSCRIPTION_PARAMETERS,
)
from swo.mpt.cli.core.products.models.parameters import (
    AgreementParametersData,
    ItemParametersData,
    RequestParametersData,
    SubscriptionParametersData,
)

DataModel = TypeVar("DataModel", bound=BaseDataModel)


class ParametersExcelFileManager(HorizontalTabFileManager, ABC, Generic[DataModel]):
    _data_model: type[DataModel]
    _sheet_name: str
    _fields = PARAMETERS_FIELDS
    _id_field = PARAMETERS_ID

    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(self._sheet_name, self._fields)


class AgreementParametersExcelFileManager(ParametersExcelFileManager):
    _data_model = AgreementParametersData
    _sheet_name = TAB_AGREEMENT_PARAMETERS


class ItemParametersExcelFileManager(ParametersExcelFileManager):
    _data_model = ItemParametersData
    _sheet_name = TAB_ITEM_PARAMETERS


class RequestParametersExcelFileManager(ParametersExcelFileManager):
    _data_model = RequestParametersData
    _sheet_name = TAB_REQUEST_PARAMETERS


class SubscriptionParametersExcelFileManager(ParametersExcelFileManager):
    _data_model = SubscriptionParametersData
    _sheet_name = TAB_SUBSCRIPTION_PARAMETERS
