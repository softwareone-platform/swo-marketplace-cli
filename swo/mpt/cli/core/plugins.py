from importlib.metadata import EntryPoint, entry_points

from typer import Typer

PLUGINS_PACKAGE = "swo.mpt.cli.plugins"


def list_entrypoints() -> list[EntryPoint]:  # pragma: no cover
    entrypoints = entry_points().select(group=PLUGINS_PACKAGE)
    if not entrypoints:
        return []

    return entrypoints


def load_plugins(app: Typer):
    for entrypoint in list_entrypoints():
        plugin_app = entrypoint.load()
        app.add_typer(plugin_app, name=entrypoint.name)
