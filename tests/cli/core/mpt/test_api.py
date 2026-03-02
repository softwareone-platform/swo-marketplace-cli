import pytest
from cli.core.errors import MPTAPIError
from cli.core.mpt.api import APIService, RelatedAPIService
from mpt_api_client.exceptions import MPTAPIError as ClientAPIError
from mpt_api_client.models import Collection, Meta, Model, Pagination
from mpt_api_client.resources.catalog.products import ProductsService
from pydantic import BaseModel
from requests_toolbelt import MultipartEncoder


class FakeModel(BaseModel):
    id: str
    name: str


class FakeApiService(APIService):
    _base_url = "fake_url"
    _api_model = FakeModel


@pytest.fixture
def collection_service(mocker):
    return mocker.MagicMock(spec=ProductsService)


@pytest.fixture
def api_service(collection_service):
    return FakeApiService(collection_service)


class FakeRelatedApiService(RelatedAPIService):
    _base_url = "fake_url/{resource_id}/action"
    _api_model = FakeModel


@pytest.fixture
def related_api_service(collection_service):
    return FakeRelatedApiService(collection_service, "fake_resource_id")


@pytest.mark.parametrize(
    ("query_params", "expected_select"),
    [
        (None, None),
        ({"select": "field1"}, "field1"),
    ],
)
def test_get(query_params, expected_select, api_service, collection_service, mocker):
    resource_mock = mocker.MagicMock(spec=Model)
    resource_mock.to_dict.return_value = {"id": "fakeId", "name": "test"}
    collection_service.get.return_value = resource_mock

    result = api_service.get("fakeId", query_params=query_params)

    assert result == {"id": "fakeId", "name": "test"}
    collection_service.get.assert_called_once_with("fakeId", select=expected_select)


@pytest.mark.parametrize(("total", "expected_response"), [(1, True), (0, False)])
def test_exists(total, expected_response, api_service, collection_service):
    collection_page = collection_service.fetch_page.return_value
    collection_page.meta.pagination.total = total

    result = api_service.exists()

    assert result is expected_response
    collection_service.fetch_page.assert_called_once_with(limit=0)


def test_list_with_query_params(mocker, api_service, collection_service):
    query_params = {"bla": "foo"}
    expected_meta_data = {"offset": 0, "limit": 100, "total": 10}
    expected_data = [{"id": "fakeId", "name": "test"}]
    resource_mock = mocker.MagicMock(spec=Model)
    resource_mock.to_dict.return_value = expected_data[0]
    collection = mocker.MagicMock(spec=Collection)
    collection.meta = mocker.MagicMock(spec=Meta)
    collection.meta.pagination = mocker.MagicMock(spec=Pagination)
    collection.meta.pagination.limit = 100
    collection.meta.pagination.offset = 0
    collection.meta.pagination.total = 10
    collection.resources = [resource_mock]
    collection_service.filter.return_value.fetch_page.return_value = collection

    result = api_service.list(query_params=query_params)

    assert result == {"meta": expected_meta_data, "data": expected_data}


def test_list_with_no_query_params(mocker, api_service, collection_service):
    query_params = None
    expected_meta_data = {"offset": 0, "limit": 100, "total": 10}
    expected_data = [{"id": "fakeId", "name": "test"}]
    resource_mock = mocker.MagicMock(spec=Model)
    resource_mock.to_dict.return_value = expected_data[0]
    collection = mocker.MagicMock(spec=Collection)
    collection.meta = mocker.MagicMock(spec=Meta)
    collection.meta.pagination = mocker.MagicMock(spec=Pagination)
    collection.meta.pagination.limit = 100
    collection.meta.pagination.offset = 0
    collection.meta.pagination.total = 10
    collection.resources = [resource_mock]
    collection_service.fetch_page.return_value = collection

    result = api_service.list(query_params=query_params)

    assert result == {"meta": expected_meta_data, "data": expected_data}


def test_list_no_data(mocker, api_service, collection_service):
    collection = mocker.MagicMock(spec=Collection)
    collection.meta = mocker.MagicMock(spec=Meta)
    collection.meta.pagination = mocker.MagicMock(spec=Pagination)
    collection.meta.pagination.limit = 100
    collection.meta.pagination.offset = 0
    collection.meta.pagination.total = 0
    collection.resources = []
    collection_service.fetch_page.return_value = collection

    result = api_service.list()

    assert result == {"meta": {"limit": 100, "offset": 0, "total": 0}, "data": []}


def test_post(mocker, api_service, collection_service):
    resource_mock = mocker.MagicMock(spec=Model)
    resource_mock.to_dict.return_value = {"id": "fakeId", "name": "test"}
    collection_service.create.return_value = resource_mock

    result = api_service.post(json={"name": "test"})

    assert result == {"id": "fakeId", "name": "test"}
    collection_service.create.assert_called_once_with({"name": "test"})


def test_post_action(api_service, collection_service):
    api_service.post_action("fake_resource_id", "publish")  # Act

    collection_service.publish.assert_called_once_with("fake_resource_id")


def test_post_action_unsupported_raises(api_service):
    with pytest.raises(MPTAPIError) as error:
        api_service.post_action("fake_resource_id", "unsupported_action")

    assert "Unsupported action 'unsupported_action'" in str(error.value)


def test_update_success(mocker, api_service, collection_service):
    resource_mock = mocker.MagicMock(spec=Model)
    resource_mock.to_dict.return_value = {"id": "fakeId", "bla": "foo", "name": "test"}
    collection_service.update.return_value = resource_mock

    result = api_service.update("fakeId", {"bla": "foo", "name": "test"})

    assert result == {"id": "fakeId", "bla": "foo", "name": "test"}
    collection_service.update.assert_called_once_with("fakeId", {"bla": "foo", "name": "test"})


def test_related_api_service(related_api_service):
    result = related_api_service.url

    assert result == "fake_url/fake_resource_id/action"


def test_api_model_property(api_service):
    result = api_service.api_model

    assert result is FakeModel


def test_url_property(api_service):
    result = api_service.url

    assert result == "fake_url"


def test_exists_with_query_params(api_service, collection_service):
    collection_filter = collection_service.filter.return_value
    collection_fetch_page = collection_filter.fetch_page.return_value
    collection_fetch_page.meta.pagination.total = 1

    result = api_service.exists(query_params={"id": "fakeId"})

    assert result is True
    collection_service.filter.assert_called_once()
    collection_service.filter.return_value.fetch_page.assert_called_once_with(limit=0)


def test_get_not_found(api_service, collection_service):
    collection_service.get.return_value = None

    with pytest.raises(MPTAPIError):
        api_service.get("missing_id")


def test_get_exception(api_service, collection_service):
    collection_service.get.side_effect = ClientAPIError(
        500, "Server Error", {"status": 500, "message": "Server Error"}
    )

    with pytest.raises(MPTAPIError):
        api_service.get("fakeId")


def test_list_with_select(mocker, api_service, collection_service):
    collection = mocker.MagicMock(spec=Collection)
    collection.meta = mocker.MagicMock(spec=Meta)
    collection.meta.pagination = mocker.MagicMock(spec=Pagination)
    collection.meta.pagination.limit = 100
    collection.meta.pagination.offset = 0
    collection.meta.pagination.total = 0
    collection.resources = []
    collection_service.select.return_value.fetch_page.return_value = collection

    result = api_service.list(query_params={"select": "field1"})

    assert result == {"meta": {"limit": 100, "offset": 0, "total": 0}, "data": []}
    collection_service.select.assert_called_once_with("field1")


def test_post_with_form_payload(mocker, api_service, collection_service):
    resource_mock = mocker.MagicMock(spec=Model)
    resource_mock.to_dict.return_value = {"id": "newId", "name": "created"}
    collection_service.create.return_value = resource_mock
    form_payload = mocker.MagicMock(spec=MultipartEncoder)
    form_payload.fields = {
        "data": '{"name": "test"}',
        "file": ("icon.png", b"file_content", "image/png"),
    }

    result = api_service.post(form_payload=form_payload)

    assert result == {"id": "newId", "name": "created"}
    collection_service.create.assert_called_once_with(
        {"name": "test"}, file=("icon.png", b"file_content", "image/png")
    )


def test_update_with_sub_resource(mocker, api_service, collection_service):
    resource_mock = mocker.MagicMock(spec=Model)
    collection_service.update_settings.return_value = resource_mock

    result = api_service.update("fakeId/settings", {"setting": "value"})

    assert result == resource_mock.to_dict()
    collection_service.update_settings.assert_called_once_with("fakeId", {"setting": "value"})


def test_exists_raises_when_meta_is_none(api_service, collection_service):
    collection_page = collection_service.fetch_page.return_value
    collection_page.meta = None

    with pytest.raises(MPTAPIError):
        api_service.exists()


def test_exists_raises_when_pagination_is_none(api_service, collection_service):
    collection_page = collection_service.fetch_page.return_value
    collection_page.meta.pagination = None

    with pytest.raises(MPTAPIError):
        api_service.exists()


def test_list_raises_when_meta_is_none(api_service, collection_service):
    collection_page = collection_service.fetch_page.return_value
    collection_page.meta = None

    with pytest.raises(MPTAPIError):
        api_service.list()


def test_list_raises_when_pagination_is_none(api_service, collection_service):
    collection_page = collection_service.fetch_page.return_value
    collection_page.meta.pagination = None

    with pytest.raises(MPTAPIError):
        api_service.list()


def test_post_form_payload_unknown_field(mocker, api_service, collection_service):
    resource_mock = mocker.MagicMock(spec=Model)
    resource_mock.to_dict.return_value = {"id": "newId", "name": "created"}
    collection_service.create.return_value = resource_mock
    form_payload = mocker.MagicMock(spec=MultipartEncoder)
    form_payload.fields = {
        "data": '{"name": "test"}',
        "file": ("icon.png", b"file_content", "image/png"),
        "ignored": 42,
    }

    result = api_service.post(form_payload=form_payload)

    assert result == {"id": "newId", "name": "created"}
    collection_service.create.assert_called_once_with(
        {"name": "test"}, file=("icon.png", b"file_content", "image/png")
    )


def test_update_unsupported_sub_resource_raises(api_service):
    with pytest.raises(MPTAPIError):
        api_service.update("fakeId/unknown", {"setting": "value"})
