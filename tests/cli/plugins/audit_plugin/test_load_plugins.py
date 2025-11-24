from importlib.metadata import EntryPoint

from cli.core.plugins import load_plugins
from cli.swocli import app
from typer.testing import CliRunner

from tests.cli.plugins import app as plugin_app

runner = CliRunner()


def test_load_plugins(mocker):
    mocker.patch.object(
        EntryPoint,
        "load",
        side_effect=lambda: plugin_app,
    )
    mocker.patch(
        "cli.core.plugins.list_entrypoints",
        return_value=[EntryPoint("tests", "tests.plugins.test_plugin", None)],
    )
    load_plugins(app)

    result = runner.invoke(app, ["tests", "test"])

    assert result.exit_code == 0, result.stdout
    assert "I'm a test plugin" in result.stdout
