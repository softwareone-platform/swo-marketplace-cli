import logging

from cli.core.state import state
from cli.swocli import app
from typer.testing import CliRunner

runner = CliRunner()


def mock_basic_config(**kwargs):
    log_handler = kwargs.get("handlers", [None])[0]
    if log_handler:
        root_logger = logging.getLogger()
        for root_handler in list(root_logger.handlers):
            root_logger.removeHandler(root_handler)
            root_handler.close()
        log_handler.setFormatter(logging.Formatter(kwargs.get("format")))
        root_logger.addHandler(log_handler)
        root_logger.setLevel(kwargs.get("level", logging.DEBUG))
        # Generate a log message immediately after setup
        root_logger.debug("Test debug message")


def test_log_file_writes_to_file(tmp_path, mocker, active_vendor_account):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[], autospec=True)
    mocker.patch(
        "cli.core.mpt.client.client_from_account",
        return_value=active_vendor_account,
        autospec=True,
    )
    log_file = tmp_path / "test.log"
    mocker.patch("logging.basicConfig", side_effect=mock_basic_config, autospec=True)

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


def test_log_file_creates_parent_directories(tmp_path, mocker, active_vendor_account):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[], autospec=True)
    mocker.patch(
        "cli.core.mpt.client.client_from_account",
        return_value=active_vendor_account,
        autospec=True,
    )
    mocker.patch("logging.basicConfig", side_effect=mock_basic_config, autospec=True)
    nested_log_file = tmp_path / "nested" / "dir" / "test.log"

    result = runner.invoke(app, ["--log-file", str(nested_log_file), "accounts", "list"])

    assert result.exit_code == 0
    assert nested_log_file.exists()
    assert nested_log_file.parent.is_dir()
    assert nested_log_file.stat().st_size > 0


def test_verbose_mode_propagates_to_client(mocker):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[], autospec=True)

    result = runner.invoke(app, ["--verbose", "accounts", "list"])

    assert result.exit_code == 0
    assert state.verbose is True


def test_no_verbose_flags_means_no_debug(caplog, mocker):
    mocker.patch("cli.core.accounts.app.list_accounts", return_value=[], autospec=True)

    with caplog.at_level(logging.DEBUG):
        result = runner.invoke(app, ["accounts", "list"])

    assert result.exit_code == 0
    assert len([record for record in caplog.records if record.levelname == "DEBUG"]) == 0
