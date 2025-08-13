from dataclasses import dataclass, field

from cli.core.models.data_model import DataCollectionModel


@dataclass(frozen=True)
class ServiceResult[DataModel, StatsCollector]:
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
    stats: StatsCollector
    model: DataModel | None

    errors: list[str] = field(default_factory=list)
    collection: DataCollectionModel | None = None
