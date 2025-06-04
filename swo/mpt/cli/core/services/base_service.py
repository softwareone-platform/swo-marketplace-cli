from abc import ABC, abstractmethod

from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.services.service_result import ServiceResult


class BaseService(ABC):
    service_context: ServiceContext

    def __init__(self, service_context: ServiceContext):
        self.account = service_context.account
        self.api = service_context.api
        self.data_model = service_context.data_model
        self.file_handler = service_context.file_handler
        self.stats = service_context.stats

    @abstractmethod
    def create(self) -> ServiceResult:  # pragma: no cover
        """
        Create a resource based on definition file

        Returns:
            ServiceResult object with operation results
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve(self) -> ServiceResult:  # pragma: no cover
        """
        Publish an existing resource

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
    def update(self, resource_id: str) -> ServiceResult:  # pragma: no cover
        """
        Update an existing resource

        Args:
            resource_id: ID of the resource to update

        Returns:
            ServiceResult object with operation results
        """
        raise NotImplementedError
