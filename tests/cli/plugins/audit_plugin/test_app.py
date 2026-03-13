import pytest
from cli.plugins.audit_plugin.app import app, compare_audit_trails
from typer.testing import CliRunner

runner = CliRunner()


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


def test_diff_by_object_id_successful_comparison(mocker, sample_audit_records):
    mock_get_records = mocker.patch(
        "cli.plugins.audit_plugin.app.get_audit_records_by_object", autospec=True
    )
    mock_create_client = mocker.patch(
        "cli.plugins.audit_plugin.app.create_api_mpt_client_from_account", autospec=True
    )
    mocker.patch("cli.plugins.audit_plugin.app.get_active_account", autospec=True)
    mock_get_records.return_value = sample_audit_records

    result = runner.invoke(app, ["diff-by-object-id", "obj123"])

    assert result.exit_code == 0
    mock_get_records.assert_called_once_with(mock_create_client.return_value, "obj123", 10)
    assert "Comparing audit trails..." in result.stdout
    assert "old_value" in result.stdout
    assert "new_value" in result.stdout


def test_diff_by_object_id_custom_positions(mocker, sample_audit_records):
    mock_get_records = mocker.patch(
        "cli.plugins.audit_plugin.app.get_audit_records_by_object", autospec=True
    )
    mocker.patch("cli.plugins.audit_plugin.app.create_api_mpt_client_from_account", autospec=True)
    mocker.patch("cli.plugins.audit_plugin.app.get_active_account", autospec=True)
    mock_get_records.return_value = sample_audit_records

    result = runner.invoke(app, ["diff-by-object-id", "obj123", "--positions", "2,1"])

    assert result.exit_code == 0
    assert "Comparing audit trails..." in result.stdout
    assert "old_value" in result.stdout
    assert "new_value" in result.stdout


def test_diff_by_object_id_insufficient_records(mocker, sample_audit_records):
    mock_get_records = mocker.patch(
        "cli.plugins.audit_plugin.app.get_audit_records_by_object", autospec=True
    )
    mocker.patch("cli.plugins.audit_plugin.app.create_api_mpt_client_from_account", autospec=True)
    mocker.patch("cli.plugins.audit_plugin.app.get_active_account", autospec=True)
    mock_get_records.return_value = [sample_audit_records[0]]

    result = runner.invoke(app, ["diff-by-object-id", "obj123"])

    assert result.exit_code == 1
    assert "Need at least 2 audit records to compare" in result.stdout


def test_diff_by_object_id_invalid_positions(mocker, sample_audit_records):
    mock_get_records = mocker.patch(
        "cli.plugins.audit_plugin.app.get_audit_records_by_object", autospec=True
    )
    mocker.patch("cli.plugins.audit_plugin.app.create_api_mpt_client_from_account", autospec=True)
    mocker.patch("cli.plugins.audit_plugin.app.get_active_account", autospec=True)
    mock_get_records.return_value = sample_audit_records

    result = runner.invoke(app, ["diff-by-object-id", "obj123", "--positions", "1,99"])

    assert result.exit_code == 1
    assert "Invalid positions" in result.stdout


def test_diff_by_records_id_successful_comparison(mocker, sample_audit_records):
    mock_get_trail = mocker.patch("cli.plugins.audit_plugin.app.get_audit_trail", autospec=True)
    mock_create_client = mocker.patch(
        "cli.plugins.audit_plugin.app.create_api_mpt_client_from_account", autospec=True
    )
    mocker.patch("cli.plugins.audit_plugin.app.get_active_account", autospec=True)
    mock_get_trail.side_effect = sample_audit_records

    result = runner.invoke(app, ["diff-by-records-id", "audit1", "audit2"])

    assert result.exit_code == 0
    mock_get_trail.assert_any_call(mock_create_client.return_value, "audit1")
    mock_get_trail.assert_any_call(mock_create_client.return_value, "audit2")
    assert "Comparing audit trails..." in result.stdout
    assert "old_value" in result.stdout
    assert "new_value" in result.stdout


def test_diff_by_records_id_different_objects(mocker):
    mock_get_trail = mocker.patch("cli.plugins.audit_plugin.app.get_audit_trail", autospec=True)
    mocker.patch("cli.plugins.audit_plugin.app.create_api_mpt_client_from_account", autospec=True)
    mocker.patch("cli.plugins.audit_plugin.app.get_active_account", autospec=True)
    mock_get_trail.side_effect = [
        {"object": {"id": "obj1"}, "timestamp": "2024-01-01T10:00:00Z"},
        {"object": {"id": "obj2"}, "timestamp": "2024-01-01T11:00:00Z"},
    ]

    result = runner.invoke(app, ["diff-by-records-id", "audit1", "audit2"])

    assert result.exit_code == 1
    assert "Cannot compare different objects" in result.stdout


def test_compare_audit_trails_no_differences(mocker):
    source = {
        "timestamp": "2024-01-01T10:00:00Z",
        "object": {"id": "obj123", "name": "Test", "value": "same"},
    }
    target = source.copy()
    mock_print = mocker.patch("cli.plugins.audit_plugin.app.console.print", autospec=True)

    compare_audit_trails(source, target)  # Act

    mock_print.assert_any_call("\n[green]No differences found between the audit trails[/green]")
