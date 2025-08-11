from dataclasses import dataclass
from typing import Generic, TypeVar

from cli.core.accounts.models import Account
from cli.core.handlers.file_manager import ExcelFileManager as BaseFileManager
from cli.core.models.data_model import DataModel
from cli.core.mpt.api import APIService as BaseAPIService
from cli.core.stats import StatsCollector

APIService = TypeVar("APIService", bound=BaseAPIService)
FileManager = TypeVar("FileManager", bound=BaseFileManager)


@dataclass(frozen=True)
class ServiceContext(Generic[APIService, DataModel, FileManager]):
    """Context object that holds dependencies for service operations."""

    account: Account
    api: APIService
    data_model: type[DataModel]
    file_manager: FileManager
    stats: StatsCollector
