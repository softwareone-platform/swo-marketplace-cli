import pytest
from cli.swocli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_cli():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "command",
    ["account", "accounts", "product", "products"],
)
def test_alias_group(command):
    # accounts and account is the same
    result = runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0


def test_alias_group_error():
    # accounts and account is the same
    result = runner.invoke(app, ["qwerty", "--help"])
    assert result.exit_code == 2


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
