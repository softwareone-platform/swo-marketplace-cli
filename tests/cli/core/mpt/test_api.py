from unittest.mock import Mock

import pytest
from cli.core.mpt.api import APIService, RelatedAPIService
from cli.core.mpt.client import MPTClient
from pydantic import BaseModel
from requests import Response


class FakeModel(BaseModel):
    id: str
    name: str


class FakeApiService(APIService):
    _base_url = "fake_url"
    _api_model = FakeModel


@pytest.fixture
def api_service(mpt_client):
    return FakeApiService(mpt_client)


class FakeRelatedApiService(RelatedAPIService):
    _base_url = "fake_url/{resource_id}/action"
    _api_model = FakeModel


@pytest.fixture
def related_api_service(mpt_client):
    return FakeRelatedApiService(mpt_client, "fake_resource_id")


@pytest.mark.parametrize(
    ("query_params", "expected_params"),
    [
        (None, {}),
        ({"bla": "foo"}, {"bla": "foo"}),
    ],
)
def test_get(query_params, expected_params, mocker, api_service):
    response_mock = Mock(spec=Response, json=Mock(return_value={"id": "fakeId", "name": "test"}))
    client_mock = mocker.patch.object(MPTClient, "get", return_value=response_mock)

    result = api_service.get("fakeId", query_params=query_params)

    assert result == {"id": "fakeId", "name": "test"}
    client_mock.assert_called_once_with("fake_url/fakeId", params=expected_params)


@pytest.mark.parametrize(("total", "expected_response"), [(1, True), (0, False)])
def test_exists(total, expected_response, mocker, api_service):
    response_mock = Mock(
        spec=Response, json=Mock(return_value={"$meta": {"pagination": {"total": total}}})
    )
    client_mock = mocker.patch.object(MPTClient, "get", return_value=response_mock)

    result = api_service.exists()

    assert result is expected_response
    client_mock.assert_called_once_with("fake_url", params={"limit": 0})


@pytest.mark.parametrize(
    ("query_params", "expected_params"),
    [
        (None, {}),
        ({"bla": "foo"}, {"bla": "foo"}),
    ],
)
def test_list(query_params, expected_params, mocker, api_service):
    expected_meta_data = {"offset": 0, "limit": 100, "total": 10}
    expected_data = [{"id": "fakeId", "name": "test"}]
    meta_data = {"pagination": expected_meta_data, "omitted": ["audit"]}
    response = {"$meta": meta_data, "data": expected_data}
    response_mock = Mock(spec=Response, json=Mock(return_value=response))
    client_mock = mocker.patch.object(MPTClient, "get", return_value=response_mock)

    result = api_service.list(query_params=query_params)

    assert result == {"meta": expected_meta_data, "data": expected_data}
    client_mock.assert_called_once_with("fake_url", params=expected_params)


def test_list_no_data(mocker, api_service):
    response_payload = {
        "$meta": {"pagination": {"offset": 0, "limit": 100, "total": 0}},
        "data": [],
    }
    response_mock = Mock(spec=Response, json=Mock(return_value=response_payload))
    client_mock = mocker.patch.object(MPTClient, "get", return_value=response_mock)

    result = api_service.list()

    assert result == {"meta": {"limit": 100, "offset": 0, "total": 0}, "data": []}
    client_mock.assert_called_once_with("fake_url", params={})


def test_post(mocker, api_service):
    response_mock = Mock(spec=Response, json=Mock(return_value={"id": "fakeId", "name": "test"}))
    client_mock = mocker.patch.object(MPTClient, "post", return_value=response_mock)

    result = api_service.post(json={"name": "test"})

    assert result == {"id": "fakeId", "name": "test"}
    client_mock.assert_called_once_with("fake_url", data=None, json={"name": "test"}, headers={})


def test_post_action(mocker, api_service):
    response_mock = Mock(spec=Response)
    client_mock = mocker.patch.object(MPTClient, "post", return_value=response_mock)

    api_service.post_action("fake_resource_id", "fake_action")  # act

    client_mock.assert_called_once_with("fake_url/fake_resource_id/fake_action")


def test_update_success(mocker, api_service):
    client_mock = mocker.patch.object(MPTClient, "put")

    api_service.update("fakeId", {"bla": "foo", "name": "test"})  # act

    client_mock.assert_called_once_with("fake_url/fakeId", json={"bla": "foo", "name": "test"})


def test_related_api_service(mocker, related_api_service):
    result = related_api_service.url

    assert result == "fake_url/fake_resource_id/action"
