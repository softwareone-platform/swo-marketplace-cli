from abc import ABC, abstractmethod
from typing import Any

from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.services.service_result import ServiceResult


class Service(ABC):
    service_context: ServiceContext

    def __init__(self, service_context: ServiceContext):
        self.account = service_context.account
        self.api = service_context.api
        self.data_model = service_context.data_model
        self.file_manager = service_context.file_manager
        self.stats = service_context.stats

    @property
    def export_params(self):
        params = {"select": "audit", "limit": 100, "offset": 0}
        params.update(self.set_export_params())
        return params

    @abstractmethod
    def create(self) -> ServiceResult:  # pragma: no cover
        """
        Create a resource based on the definition file

        Returns:
            ServiceResult object with operation results
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve(self) -> ServiceResult:  # pragma: no cover
        """
        Retrieve an existing resource from the file

        Returns:
            ServiceResult object with operation results
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:  # pragma: no cover
        """
        Retrieve a resource from MPT by its ID

        Args:
            resource_id: ID of the resource to retrieve

        Returns:
            ServiceResult object with operation results
        """
        raise NotImplementedError

    @abstractmethod
    def update(self) -> ServiceResult:  # pragma: no cover
        """
        Update an existing resource

        Returns:
            ServiceResult object with operation results
        """
        raise NotImplementedError

    def set_export_params(self) -> dict[str, Any]:
        """
        Override this method to set the export parameters
        """
        return {}

    def _set_error(self, error: str, resource_id: str | None = None) -> None:
        self.file_manager.write_error(error, resource_id)
        self.stats.add_error(self.file_manager.tab_name)

    def _set_synced(self, resource_id: str, item_coordinate: str) -> None:
        self.file_manager.write_id(item_coordinate, resource_id)
        self.stats.add_synced(self.file_manager.tab_name)

    def _set_skipped(self):
        self.stats.add_skipped(self.file_manager.tab_name)


class BaseService(Service, ABC):
    @abstractmethod
    def export(self, resource_id: str) -> ServiceResult:  # pragma: no cover
        """
        Export a resource from mpt to the file

        Args:
            resource_id: The ID of the product to export.

        Returns:
            ServiceResult object with operation results
        """
        raise NotImplementedError


class RelatedBaseService(Service, ABC):
    @property
    def resource_id(self):
        return self.api.resource_id

    @abstractmethod
    def export(self) -> ServiceResult:  # pragma: no cover
        """
        Export a resource from mpt to the file

        Returns:
            ServiceResult object with operation results
        """
        raise NotImplementedError
