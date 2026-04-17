import pytest
from cli.plugins.audit_plugin.api import (
    get_audit_records_by_object,
    get_audit_trail,
)
from mpt_api_client import MPTClient, RQLQuery
from mpt_api_client.models.model import Model
from typer import Exit


def _mock_record(mocker, record_data: dict):
    record = mocker.MagicMock(spec=Model)
    record.to_dict.return_value = record_data
    return record


@pytest.fixture
def mock_client(mocker):
    return mocker.Mock(spec=MPTClient)


def test_get_audit_trail_successful_retrieval(mock_client, mocker):
    expected_record = {
        "id": "audit123",
        "object": {"id": "obj123"},
        "actor": {"name": "Test User"},
    }
    records_options = mock_client.audit.records.options
    filtered = records_options.return_value.filter.return_value
    chain = filtered.select.return_value
    chain.fetch_page.return_value = [_mock_record(mocker, expected_record)]

    result = get_audit_trail(mock_client, "audit123")

    select_fields = ["object", "actor", "details", "documents", "request.api.geolocation"]
    assert result == expected_record
    records_options.assert_called_once_with(render=True)
    records_options.return_value.filter.assert_called_once_with(RQLQuery(id="audit123"))
    filtered.select.assert_called_once_with(*select_fields)
    chain.fetch_page.assert_called_once_with(limit=1)


def test_get_audit_trail_no_record_found(mock_client):
    records_options = mock_client.audit.records.options
    filtered = records_options.return_value.filter.return_value
    chain = filtered.select.return_value
    chain.fetch_page.return_value = []

    with pytest.raises(Exit):
        get_audit_trail(mock_client, "audit123")


def test_get_audit_trail_api_error(mock_client):
    records_options = mock_client.audit.records.options
    filtered = records_options.return_value.filter.return_value
    filtered.select.return_value.fetch_page.side_effect = Exception("API Error")

    with pytest.raises(Exit):
        get_audit_trail(mock_client, "audit123")


def test_get_audit_records_by_object_retrieval(mock_client, mocker):
    expected_records = [
        {"id": "audit1", "object": {"id": "obj123"}, "timestamp": "2024-01-01T10:00:00Z"},
        {"id": "audit2", "object": {"id": "obj123"}, "timestamp": "2024-01-01T11:00:00Z"},
    ]
    records_options = mock_client.audit.records.options
    filtered = records_options.return_value.filter.return_value
    chain = filtered.order_by.return_value.select.return_value
    chain.fetch_page.return_value = [_mock_record(mocker, rec) for rec in expected_records]

    result = get_audit_records_by_object(mock_client, "obj123", limit=10)

    select_fields = ["object", "actor", "details", "documents", "request.api.geolocation"]
    assert result == expected_records
    records_options.assert_called_once_with(render=True)
    records_options.return_value.filter.assert_called_once_with(RQLQuery(object__id="obj123"))
    filtered.order_by.assert_called_once_with("-timestamp")
    filtered.order_by.return_value.select.assert_called_once_with(*select_fields)
    chain.fetch_page.assert_called_once_with(limit=10)


def test_get_audit_records_by_object_empty(mock_client):
    records_options = mock_client.audit.records.options
    filtered = records_options.return_value.filter.return_value
    chain = filtered.order_by.return_value.select.return_value
    chain.fetch_page.return_value = []

    with pytest.raises(Exit):
        get_audit_records_by_object(mock_client, "obj123")


def test_get_audit_records_by_object_api_error(mock_client):
    records_options = mock_client.audit.records.options
    filtered = records_options.return_value.filter.return_value
    chain = filtered.order_by.return_value.select.return_value
    chain.fetch_page.side_effect = Exception("API Error")

    with pytest.raises(Exit):
        get_audit_records_by_object(mock_client, "obj123")


def test_get_audit_records_by_object_custom_limit(mock_client, mocker):
    records_options = mock_client.audit.records.options
    filtered = records_options.return_value.filter.return_value
    chain = filtered.order_by.return_value.select.return_value
    chain.fetch_page.return_value = [_mock_record(mocker, {"id": "audit1"})]

    result = get_audit_records_by_object(mock_client, "obj123", limit=5)

    chain.fetch_page.assert_called_once_with(limit=5)
    assert result == [{"id": "audit1"}]
