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


def test_log_file_writes_to_file(tmp_path, mocker):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[])
    mock_account = create_mock_account()
    mocker.patch("cli.core.mpt.client.client_from_account", return_value=mock_account)
    log_file = tmp_path / "test.log"

    # BL
    def mock_basic_config(**kwargs):
        log_handler = kwargs.get("handlers", [None])[0]
        if log_handler:
            log_handler.setFormatter(logging.Formatter(kwargs.get("format")))
            logging.getLogger().addHandler(log_handler)
            logging.getLogger().setLevel(kwargs.get("level", logging.DEBUG))
            # Generate a log message immediately after setup
            logging.getLogger().debug("Test debug message")

    # BL
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

    # BL
    def mock_basic_config(**kwargs):
        log_handler = kwargs.get("handlers", [None])[0]
        if log_handler:
            log_handler.setFormatter(logging.Formatter(kwargs.get("format")))
            logging.getLogger().addHandler(log_handler)
            logging.getLogger().setLevel(kwargs.get("level", logging.DEBUG))
            # Generate a log message immediately after setup
            logging.getLogger().debug("Test debug message")

    # BL
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
