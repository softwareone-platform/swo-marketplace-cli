from importlib.metadata import EntryPoint, entry_points

from typer import Typer

PLUGINS_PACKAGE = "cli.plugins"


def list_entrypoints() -> list[EntryPoint]:
    """List all entry points for the plugins package.

    Returns:
        A list of EntryPoint objects registered under the plugins package group.

    """
    entrypoints = entry_points().select(group=PLUGINS_PACKAGE)
    if not entrypoints:
        return []
    return list(entrypoints)


def load_plugins(app: Typer) -> None:
    """Load and register plugins as Typer subcommands.

    Args:
        app: The main Typer application to which plugins will be added.

    """
    for entrypoint in list_entrypoints():
        plugin_app = entrypoint.load()
        app.add_typer(plugin_app, name=entrypoint.name)
