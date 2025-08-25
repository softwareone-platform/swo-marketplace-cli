from dataclasses import dataclass

from cli.core.accounts.models import Account
from cli.core.stats import StatsCollector


@dataclass(frozen=True)
class ServiceContext[APIService, DataModel, ExcelFileManager]:
    """Context object that holds dependencies for service operations."""

    account: Account
    api: APIService
    data_model: type[DataModel]
    file_manager: ExcelFileManager
    stats: StatsCollector
