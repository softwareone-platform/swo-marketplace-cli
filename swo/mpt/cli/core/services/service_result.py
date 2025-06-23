from dataclasses import dataclass, field
from typing import Generic, TypeVar

from swo.mpt.cli.core.models.data_model import DataCollectionModel, DataModel
from swo.mpt.cli.core.stats import StatsCollector

Stats = TypeVar("Stats", bound=StatsCollector)


@dataclass(frozen=True)
class ServiceResult(Generic[DataModel, Stats]):
    """
    Represents the result of a service operation.

    Attributes:
        success: Indicates if the operation was successful.
        errors: List of error messages if the operation failed.
        stats: Statistics collected during the operation.
        model: The data model returned by the service, if applicable.
        collection: The data collection returned by the service, if applicable.
    """

    success: bool
    stats: Stats
    model: DataModel | None

    errors: list[str] = field(default_factory=list)
    collection: DataCollectionModel | None = None
