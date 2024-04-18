from importlib.metadata import PackageNotFoundError, version
from typing import Annotated, Optional

import typer
from swo.mpt.cli.core.accounts import app as accounts_app
from swo.mpt.cli.core.alias_group import AliasTyperGroup
from swo.mpt.cli.core.console import console, show_banner

app = typer.Typer(cls=AliasTyperGroup, callback=show_banner)
app.add_typer(accounts_app, name="accounts")


try:
    VERSION = version("swo-marketplace-cli")
except PackageNotFoundError:
    VERSION = "unknown"


__version__ = VERSION


def get_version():
    return __version__


def version_callback(value: bool):
    show_banner()
    if value:
        console.print(f"version: {get_version()}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    pass


if __name__ == "__main__":
    app()
