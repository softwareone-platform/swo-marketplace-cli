from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.mpt.api import APIService as BaseAPIService
from swo.mpt.cli.core.stats import StatsCollector

APIService = TypeVar("APIService", bound=BaseAPIService)
DataModel = TypeVar("DataModel", bound=BaseDataModel)


@dataclass(frozen=True)
class ServiceContext(Generic[APIService, DataModel]):
    account: Account
    api: APIService
    data_model: type[DataModel]
    file_handler: Any  # TODO: typing
    stats: StatsCollector
