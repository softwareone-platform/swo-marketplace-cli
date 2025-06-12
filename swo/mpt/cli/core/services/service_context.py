from dataclasses import dataclass
from typing import Generic, TypeVar

from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.handlers.file_manager import ExcelFileManager as BaseFileManager
from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.mpt.api import APIService as BaseAPIService
from swo.mpt.cli.core.stats import StatsCollector

APIService = TypeVar("APIService", bound=BaseAPIService)
DataModel = TypeVar("DataModel", bound=BaseDataModel)
FileManager = TypeVar("FileManager", bound=BaseFileManager)


@dataclass(frozen=True)
class ServiceContext(Generic[APIService, DataModel, FileManager]):
    account: Account
    api: APIService
    data_model: type[DataModel]
    file_manager: FileManager
    stats: StatsCollector
