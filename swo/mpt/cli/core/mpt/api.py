from abc import ABC
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from swo.mpt.cli.core.errors import MPTAPIError, wrap_http_error
from swo.mpt.cli.core.mpt.client import MPTClient
from swo.mpt.cli.core.mpt.models import Meta

APIModel = TypeVar("APIModel", bound=BaseModel)


class APIService(ABC, Generic[APIModel]):
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

        self.api_model.model_validate(data)
        return data

    @wrap_http_error
    def list(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
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
        headers = headers or {}
        response = self.client.post(self.url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return self.api_model.model_validate(response.json(), by_alias=True).model_dump()

    @wrap_http_error
    def post_action(self, resource_id: str, action: str) -> None:
        response = self.client.post(f"{self.url}{resource_id}/{action}")
        response.raise_for_status()

    @wrap_http_error
    def update(self, resource_id: str, data: dict[str, Any]) -> None:
        response = self.client.put(f"{self.url}{resource_id}", json=data)
        response.raise_for_status()


class RelatedAPIService(APIService, ABC):
    def __init__(self, client, resource_id: str):
        super().__init__(client)
        self.resource_id = resource_id

    @property
    def url(self) -> str:
        return self._base_url.format(resource_id=self.resource_id)
