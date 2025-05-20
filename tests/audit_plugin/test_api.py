from unittest.mock import Mock

import pytest
from swo.mpt.cli.plugins.audit_plugin.api import (
    get_audit_records_by_object,
    get_audit_trail,
)
from typer import Exit


@pytest.fixture
def mock_client():
    client = Mock()
    client.get = Mock()
    return client


@pytest.fixture
def mock_response():
    response = Mock()
    response.json = Mock()
    return response


class TestGetAuditTrail:
    def test_successful_retrieval(self, mock_client, mock_response):
        # Setup
        expected_data = {
            "id": "audit123",
            "object": {"id": "obj123"},
            "actor": {"name": "Test User"},
        }
        mock_response.json.return_value = expected_data
        mock_client.get.return_value = mock_response

        # Execute
        result = get_audit_trail(mock_client, "audit123")

        # Assert
        assert result == expected_data
        mock_client.get.assert_called_once()
        called_endpoint = mock_client.get.call_args[0][0]
        assert "/audit/records/audit123" in called_endpoint
        assert "render()" in called_endpoint
        assert "select=object,actor,details,documents,request.api.geolocation" in called_endpoint

    def test_api_error(self, mock_client):
        # Setup
        mock_client.get.side_effect = Exception("API Error")

        # Execute and Assert
        with pytest.raises(Exit):
            get_audit_trail(mock_client, "audit123")
        mock_client.get.assert_called_once()

    def test_json_decode_error(self, mock_client, mock_response):
        # Setup
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.get.return_value = mock_response

        # Execute and Assert
        with pytest.raises(Exit):
            get_audit_trail(mock_client, "audit123")


class TestGetAuditRecordsByObject:
    def test_successful_retrieval(self, mock_client, mock_response):
        # Setup
        expected_data = {
            "data": [
                {
                    "id": "audit1",
                    "object": {"id": "obj123"},
                    "timestamp": "2024-01-01T10:00:00Z",
                },
                {
                    "id": "audit2",
                    "object": {"id": "obj123"},
                    "timestamp": "2024-01-01T11:00:00Z",
                },
            ]
        }
        mock_response.json.return_value = expected_data
        mock_client.get.return_value = mock_response

        # Execute
        result = get_audit_records_by_object(mock_client, "obj123", limit=10)

        # Assert
        assert result == expected_data["data"]
        mock_client.get.assert_called_once()
        called_endpoint = mock_client.get.call_args[0][0]
        assert "/audit/records" in called_endpoint
        assert "render()" in called_endpoint
        assert "eq(object.id,obj123)" in called_endpoint
        assert "limit=10" in called_endpoint

    def test_no_records_found(self, mock_client, mock_response):
        # Setup
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response

        # Execute and Assert
        with pytest.raises(Exit):
            get_audit_records_by_object(mock_client, "obj123")
        mock_client.get.assert_called_once()

    def test_api_error(self, mock_client):
        # Setup
        mock_client.get.side_effect = Exception("API Error")

        # Execute and Assert
        with pytest.raises(Exit):
            get_audit_records_by_object(mock_client, "obj123")
        mock_client.get.assert_called_once()

    def test_json_decode_error(self, mock_client, mock_response):
        # Setup
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client.get.return_value = mock_response

        # Execute and Assert
        with pytest.raises(Exit):
            get_audit_records_by_object(mock_client, "obj123")

    def test_custom_limit(self, mock_client, mock_response):
        # Setup
        mock_response.json.return_value = {"data": [{"id": "audit1"}]}
        mock_client.get.return_value = mock_response

        # Execute
        get_audit_records_by_object(mock_client, "obj123", limit=5)

        # Assert
        called_endpoint = mock_client.get.call_args[0][0]
        assert "limit=5" in called_endpoint
