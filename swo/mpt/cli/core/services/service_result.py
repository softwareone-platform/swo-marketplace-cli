from dataclasses import dataclass, field
from typing import Generic, TypeVar

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.stats import StatsCollector

DataModel = TypeVar("DataModel", bound=BaseDataModel)
Stats = TypeVar("Stats", bound=StatsCollector)


@dataclass(frozen=True)
class ServiceResult(Generic[DataModel, Stats]):
    """
    Represents the result of a service operation.

    Attributes:
        success (bool): Indicates if the operation was successful.
        errors (list[str]): List of error messages if the operation failed.
        stats (Stats): Statistics collected during the operation.
        model (DataModel | None): The data model returned by the service, if applicable.
    """

    success: bool
    stats: Stats
    model: DataModel | None

    errors: list[str] = field(default_factory=list)
