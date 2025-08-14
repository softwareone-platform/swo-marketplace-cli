from abc import ABC
from typing import TYPE_CHECKING, Any

from cli.core.errors import MPTAPIError, wrap_http_error
from cli.core.mpt.client import MPTClient
from cli.core.mpt.models import Meta

if TYPE_CHECKING:
    from cli.core.mpt.models import BaseModel


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
        self.client = client

    @property
    def api_model(self) -> APIModel:
        return self._api_model

    @property
    def url(self) -> str:
        return self._base_url

    @wrap_http_error
    def exists(self, params: dict[str, Any] | None = None) -> bool:
        """Check if any resources exist matching the given parameters.

        Args:
            params: Optional query parameters for the request.

        Returns:
            True if at least one resource exists, False otherwise.

        """
        params = params or {}
        params["limit"] = 0
        response = self.client.get(f"{self.url}", params=params)
        response.raise_for_status()
        return response.json()["$meta"]["pagination"]["total"] > 0

    @wrap_http_error
    def get(self, resource_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Retrieve a resource by its ID.

        Args:
            resource_id: The unique identifier of the resource.
            params: Optional query parameters for the request.

        Returns:
            The resource data as a dictionary.

        Raises:
            MPTAPIError: If the resource is not found.

        """
        params = params or {}
        response = self.client.get(f"{self.url}/{resource_id}", params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise MPTAPIError(
                f"Resource with ID {resource_id} not found at {self.url}", "404 not found"
            )
        self.api_model.model_validate(data)
        return data

    @wrap_http_error
    def list(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """List resources with optional query parameters.

        Args:
            params: Optional query parameters for the request.

        Returns:
            A dictionary containing meta information and the list of resources.

        """
        params = params or {}
        response = self.client.get(self.url, params=params)
        response.raise_for_status()
        json_body = response.json()
        meta = Meta.model_validate(json_body["$meta"]["pagination"])
        return {"meta": meta.model_dump(), "data": json_body["data"]}

    @wrap_http_error
    def post(
        self,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new resource.

        Args:
            data: Form data to send in the request body.
            json: JSON data to send in the request body.
            headers: Optional headers for the request.

        Returns:
            The created resource as a dictionary.

        """
        headers = headers or {}
        response = self.client.post(self.url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return self.api_model.model_validate(response.json(), by_alias=True).model_dump()

    @wrap_http_error
    def post_action(self, resource_id: str, action: str) -> None:
        """Perform an action on a specific resource.

        Args:
            resource_id: The unique identifier of the resource.
            action: The action to perform.

        """
        response = self.client.post(f"{self.url}/{resource_id}/{action}")
        response.raise_for_status()

    @wrap_http_error
    def update(self, resource_id: str, data: dict[str, Any]) -> None:
        """Update a resource by its ID.

        Args:
            resource_id: The unique identifier of the resource.
            data: The data to update the resource with.

        """
        response = self.client.put(f"{self.url}/{resource_id}", json=data)
        response.raise_for_status()


class RelatedAPIService(APIService, ABC):
    """Abstract base class for related API service operations."""

    def __init__(self, client, resource_id: str):
        super().__init__(client)
        self.resource_id = resource_id

    @property
    def url(self) -> str:
        return self._base_url.format(resource_id=self.resource_id)
