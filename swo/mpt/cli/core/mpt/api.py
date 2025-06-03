from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from swo.mpt.cli.core.errors import MPTAPIError, wrap_http_error
from swo.mpt.cli.core.mpt.client import MPTClient

APIModel = TypeVar("APIModel", bound=BaseModel)


class APIService(Generic[APIModel]):
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
        params = params or {}

        params["limit"] = 0
        response = self.client.get(f"{self.url}", params=params)
        response.raise_for_status()
        return response.json()["$meta"]["pagination"]["total"] > 0

    @wrap_http_error
    def get(self, resource_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}

        response = self.client.get(f"{self.url}{resource_id}", params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise MPTAPIError(
                f"Resource with ID {resource_id} not found at {self.url}", "404 not found"
            )

        return self.api_model.model_validate(response.json()).model_dump()

    @wrap_http_error
    def list(self, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        params = params or {}

        response = self.client.get(self.url, params=params)
        response.raise_for_status()
        data = response.json()["data"]
        if not data:
            return []

        return [self.api_model.model_validate(resource).model_dump() for resource in data]

    @wrap_http_error
    def post(self, data: dict[str, Any]) -> dict[str, Any]:
        response = self.client.post(self.url, json=data)
        response.raise_for_status()
        return self.api_model.model_validate(response.json()).model_dump()

    @wrap_http_error
    def update(self, resource_id: str, data: dict[str, Any]) -> None:
        response = self.client.put(f"{self.url}{resource_id}", json=data)
        response.raise_for_status()
