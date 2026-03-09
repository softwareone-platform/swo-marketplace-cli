import json as json_module
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from cli.core.errors import MPTAPIError, wrap_mpt_api_error
from mpt_api_client import MPTClient, RQLQuery

if TYPE_CHECKING:
    from pydantic import BaseModel


class APIService[APIModel: "BaseModel"](ABC):
    """Abstract base class for API service operations.

    This class provides common functionality for API services that interact
    with MPT endpoints, including CRUD operations and error handling.

    Attributes:
        _base_url: Base URL for the API endpoint.
        _api_model:  Model for API response validation.

    """

    _base_url: str
    _api_model: APIModel

    def __init__(self, client: MPTClient):
        self._client = client

    @property
    @abstractmethod
    def api_collection(self):
        raise NotImplementedError

    @property
    def client(self) -> MPTClient:
        return self._client

    @property
    def api_model(self) -> APIModel:
        return self._api_model

    @property
    def url(self) -> str:
        return self._base_url

    @wrap_mpt_api_error
    def exists(self, query_params: dict[str, Any] | None = None) -> bool:
        """Check if any resources exist matching the given parameters.

        Args:
            query_params: Optional query parameters for the request.

        Returns:
            True if at least one resource exists, False otherwise.

        """
        service = self.api_collection
        if query_params:
            service = service.filter(RQLQuery(**query_params))
        service_collection_data = service.fetch_page(limit=0)
        if service_collection_data.meta is None or service_collection_data.meta.pagination is None:
            raise MPTAPIError("Missing pagination metadata in response.", "Invalid response")
        return service_collection_data.meta.pagination.total > 0

    @wrap_mpt_api_error
    def get(
        self,
        resource_id: str,
        query_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Retrieve a resource by its ID.

        Args:
            resource_id: The unique identifier of the resource.
            query_params: Optional query parameters for the request.

        Returns:
            The resource data as a dictionary.

        Raises:
            MPTAPIError: If the resource is not found.

        """
        select_value = (query_params or {}).get("select")
        resource_data = self.api_collection.get(resource_id, select=select_value)
        if not resource_data:
            raise MPTAPIError(
                f"Resource with ID {resource_id} not found at {self.url}", "404 not found"
            )
        return resource_data.to_dict()

    @wrap_mpt_api_error
    def list(self, query_params: dict[str, Any] | None = None) -> dict[str, Any]:
        """List resources with optional query parameters.

        Args:
            query_params: Optional query parameters for the request.

        Returns:
            A dictionary containing meta information and the list of resources.

        """
        query_params = dict(query_params or {})
        limit = query_params.pop("limit", 100)
        offset = query_params.pop("offset", 0)
        select = query_params.pop("select", None)
        service = self.api_collection

        if query_params:
            service = service.filter(RQLQuery(**query_params))
        if select:
            service = service.select(select)

        collection = service.fetch_page(limit=limit, offset=offset)
        if collection.meta is None or collection.meta.pagination is None:
            raise MPTAPIError("Missing pagination metadata in response.", "Invalid response")
        pagination = collection.meta.pagination
        return {
            "meta": {
                "limit": pagination.limit,
                "offset": pagination.offset,
                "total": pagination.total,
            },
            "data": [resource.to_dict() for resource in collection.resources],
        }

    @wrap_mpt_api_error
    def post(
        self,
        form_payload: Any | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new resource.

        Args:
            form_payload: Form data to send in the request body.
            json: JSON data to send in the request body.
            headers: Optional headers for the request.

        Returns:
            The created resource as a dictionary.

        """
        headers = headers or {}

        if form_payload is None:
            created_resource = self.api_collection.create(json)
        else:
            json_data = None
            file_data = None
            for form_value in form_payload.fields.values():
                if isinstance(form_value, tuple):
                    file_data = form_value
                elif isinstance(form_value, str):
                    json_data = json_module.loads(form_value)
            created_resource = self.api_collection.create(json_data, file=file_data)

        return created_resource.to_dict()

    @wrap_mpt_api_error
    def post_action(self, resource_id: str, action: str) -> None:
        """Perform an action on a specific resource.

        Args:
            resource_id: The unique identifier of the resource.
            action: The action to perform.

        """
        action_handler = getattr(self.api_collection, action, None)
        if action_handler is None:
            raise MPTAPIError(f"Unsupported action '{action}' at {self.url}", "400 bad request")
        return action_handler(resource_id)

    @wrap_mpt_api_error
    def update(self, resource_id: str, json_payload: dict[str, Any]) -> None:
        """Update a resource by its ID.

        Args:
            resource_id: The unique identifier of the resource.
            json_payload: The data to update the resource with.

        """
        if "/" in resource_id:
            base_id, sub_resource = resource_id.split("/", 1)
            updater = getattr(self.api_collection, f"update_{sub_resource}", None)
            if updater is None:
                raise MPTAPIError(
                    f"Unsupported sub-resource update '{sub_resource}' at {self.url}",
                    "400 bad request",
                )
            updated_resource = updater(base_id, json_payload)
        else:
            updated_resource = self.api_collection.update(resource_id, json_payload)

        return updated_resource.to_dict()


class RelatedAPIService(APIService, ABC):
    """Abstract base class for related API service operations."""

    def __init__(self, client: MPTClient, resource_id: str):
        super().__init__(client)
        self.resource_id = resource_id

    @property
    def url(self) -> str:
        return self._base_url.format(resource_id=self.resource_id)
