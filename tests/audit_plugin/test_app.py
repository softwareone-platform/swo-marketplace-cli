from unittest.mock import Mock, patch

import pytest
from swo.mpt.cli.plugins.audit_plugin.app import app, compare_audit_trails
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def mock_get_active_account():
    return Mock()


@pytest.fixture
def mock_client_from_account():
    return Mock()


@pytest.fixture
def sample_audit_records():
    return [
        {
            "id": "audit1",
            "timestamp": "2024-01-01T10:00:00Z",
            "object": {
                "id": "obj123",
                "name": "Test Object",
                "objectType": "TestType",
                "value": "old_value",
            },
        },
        {
            "id": "audit2",
            "timestamp": "2024-01-02T10:00:00Z",
            "object": {
                "id": "obj123",
                "name": "Test Object",
                "objectType": "TestType",
                "value": "new_value",
            },
        },
    ]


class TestDiffByObjectId:
    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_active_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.client_from_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_audit_records_by_object")
    def test_successful_comparison(
        self,
        mock_get_records,
        mock_client_from_account,
        mock_get_active_account,
        sample_audit_records,
    ):
        # Setup
        mock_get_records.return_value = sample_audit_records

        # Execute
        result = runner.invoke(app, ["diff-by-object-id", "obj123"])

        # Assert
        assert result.exit_code == 0
        mock_get_records.assert_called_once_with(
            mock_client_from_account.return_value, "obj123", 10
        )
        assert "Comparing audit trails..." in result.stdout
        assert "old_value" in result.stdout
        assert "new_value" in result.stdout

    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_active_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.client_from_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_audit_records_by_object")
    def test_with_custom_positions(
        self,
        mock_get_records,
        mock_client_from_account,
        mock_get_active_account,
        sample_audit_records,
    ):
        # Setup
        mock_get_records.return_value = sample_audit_records

        # Execute
        result = runner.invoke(app, ["diff-by-object-id", "obj123", "--positions", "2,1"])

        # Assert
        assert result.exit_code == 0
        assert "Comparing audit trails..." in result.stdout
        assert "old_value" in result.stdout
        assert "new_value" in result.stdout

    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_active_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.client_from_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_audit_records_by_object")
    def test_insufficient_records(
        self,
        mock_get_records,
        mock_client_from_account,
        mock_get_active_account,
        sample_audit_records,
    ):
        # Setup
        mock_get_records.return_value = [sample_audit_records[0]]

        # Execute
        result = runner.invoke(app, ["diff-by-object-id", "obj123"])

        # Assert
        assert result.exit_code == 1
        assert "Need at least 2 audit records to compare" in result.stdout

    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_active_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.client_from_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_audit_records_by_object")
    def test_invalid_positions(
        self,
        mock_get_records,
        mock_client_from_account,
        mock_get_active_account,
        sample_audit_records,
    ):
        # Setup
        mock_get_records.return_value = sample_audit_records

        # Execute
        result = runner.invoke(app, ["diff-by-object-id", "obj123", "--positions", "1,99"])

        # Assert
        assert result.exit_code == 1
        assert "Invalid positions" in result.stdout


class TestDiffByRecordsId:
    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_active_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.client_from_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_audit_trail")
    def test_successful_comparison(
        self,
        mock_get_trail,
        mock_client_from_account,
        mock_get_active_account,
        sample_audit_records,
    ):
        # Setup
        mock_get_trail.side_effect = sample_audit_records

        # Execute
        result = runner.invoke(app, ["diff-by-records-id", "audit1", "audit2"])

        # Assert
        assert result.exit_code == 0
        assert "Comparing audit trails..." in result.stdout
        assert "old_value" in result.stdout
        assert "new_value" in result.stdout

    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_active_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.client_from_account")
    @patch("swo.mpt.cli.plugins.audit_plugin.app.get_audit_trail")
    def test_different_objects(
        self, mock_get_trail, mock_client_from_account, mock_get_active_account
    ):
        # Setup
        mock_get_trail.side_effect = [
            {"object": {"id": "obj1"}, "timestamp": "2024-01-01T10:00:00Z"},
            {"object": {"id": "obj2"}, "timestamp": "2024-01-01T11:00:00Z"},
        ]

        # Execute
        result = runner.invoke(app, ["diff-by-records-id", "audit1", "audit2"])

        # Assert
        assert result.exit_code == 1
        assert "Cannot compare different objects" in result.stdout


def test_compare_audit_trails_no_differences():
    source = {
        "timestamp": "2024-01-01T10:00:00Z",
        "object": {"id": "obj123", "name": "Test", "value": "same"},
    }
    target = source.copy()

    # Execute
    with patch("swo.mpt.cli.plugins.audit_plugin.app.console.print") as mock_print:
        compare_audit_trails(source, target)

    # Assert
    mock_print.assert_any_call("\n[green]No differences found between the audit trails[/green]")
