import logging

from cli.core.accounts.models import Account
from cli.core.state import state
from cli.swocli import app
from typer.testing import CliRunner

runner = CliRunner()


def create_mock_account():
    return Account(
        id="test-id",
        name="test-account",
        type="test-type",
        environment="test",
        token="test-token",  # noqa: S106
        token_id="test-token-id",  # noqa: S106
    )


def test_verbose_flag_enables_logging(caplog, requests_mocker):
    data = {
        "$meta": {
            "pagination": {"offset": 0, "limit": 10, "total": 1},
            "omitted": ["modules", "audit"],
        },
        "data": [
            {
                "id": "TKN-1234-5678",
                "href": "/accounts/api-tokens/TKN-1234-5678",
                "status": "Active",
                "name": "Test API Token",
                "description": "Token for testing purposes",
                "icon": "",
                "lastAccessAt": "2024-03-15T10:00:00.000Z",
                "token": "idt:TKN-1234-5678:abc123",
                "account": {
                    "id": "ACC-8765-4321",
                    "href": "/accounts/accounts/ACC-8765-4321",
                    "type": "Development",
                    "status": "Active",
                    "icon": "/v1/accounts/accounts/ACC-8765-4321/icon",
                    "name": "TestCompany",
                },
            }
        ],
    }
    requests_mocker.add(
        requests_mocker.GET,
        "https://api.platform.softwareone.com/public/v1/accounts/api-tokens?limit=2&token=test_token",
        json=data,
        status=200,
    )
    with caplog.at_level(logging.DEBUG):
        runner.invoke(app, ["--verbose", "accounts", "add", "test_token"])

    assert len(caplog.records) > 0
    assert any("GET" in record.message for record in caplog.records)
    assert any("/accounts" in record.message for record in caplog.records)


def test_log_file_writes_to_file(tmp_path, mocker):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[])
    mock_account = create_mock_account()
    mocker.patch("cli.core.mpt.client.client_from_account", return_value=mock_account)

    log_file = tmp_path / "test.log"

    def mock_basic_config(**kwargs):
        handler = kwargs.get("handlers", [None])[0]
        if handler:
            handler.setFormatter(logging.Formatter(kwargs.get("format")))
            logging.getLogger().addHandler(handler)
            logging.getLogger().setLevel(kwargs.get("level", logging.DEBUG))
            # Generate a log message immediately after setup
            logging.getLogger().debug("Test debug message")

    mocker.patch("logging.basicConfig", side_effect=mock_basic_config)

    result = runner.invoke(app, ["--log-file", str(log_file), "accounts", "list"])

    assert result.exit_code == 0
    assert log_file.exists()
    assert log_file.stat().st_size > 0
    log_content = log_file.read_text()
    assert "Test debug message" in log_content


def test_verbose_and_log_file_are_exclusive():
    result = runner.invoke(app, ["--verbose", "--log-file", "test.log", "accounts", "list"])

    assert result.exit_code == 1
    assert "Cannot use both --verbose and --log-file together" in result.stdout


def test_log_file_creates_parent_directories(tmp_path, mocker):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[])
    mock_account = create_mock_account()
    mocker.patch("cli.core.mpt.client.client_from_account", return_value=mock_account)

    def mock_basic_config(**kwargs):
        handler = kwargs.get("handlers", [None])[0]
        if handler:
            handler.setFormatter(logging.Formatter(kwargs.get("format")))
            logging.getLogger().addHandler(handler)
            logging.getLogger().setLevel(kwargs.get("level", logging.DEBUG))
            # Generate a log message immediately after setup
            logging.getLogger().debug("Test debug message")

    mocker.patch("logging.basicConfig", side_effect=mock_basic_config)

    nested_log_file = tmp_path / "nested" / "dir" / "test.log"

    result = runner.invoke(app, ["--log-file", str(nested_log_file), "accounts", "list"])

    assert result.exit_code == 0
    assert nested_log_file.exists()
    assert nested_log_file.parent.is_dir()
    assert nested_log_file.stat().st_size > 0


def test_verbose_mode_propagates_to_client(mocker):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[])

    result = runner.invoke(app, ["--verbose", "accounts", "list"])

    assert result.exit_code == 0
    assert state.verbose is True


def test_no_verbose_flags_means_no_debug(caplog, mocker):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[])

    with caplog.at_level(logging.DEBUG):
        result = runner.invoke(app, ["accounts", "list"])

    assert result.exit_code == 0
    assert len([r for r in caplog.records if r.levelname == "DEBUG"]) == 0
