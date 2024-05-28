from importlib.metadata import PackageNotFoundError, version
from typing import Annotated, Optional

import typer
from swo.mpt.cli.core.accounts import app as accounts_app
from swo.mpt.cli.core.alias_group import AliasTyperGroup
from swo.mpt.cli.core.console import console, show_banner
from swo.mpt.cli.core.plugins import load_plugins
from swo.mpt.cli.core.pricelists import app as pricelists_app
from swo.mpt.cli.core.products import app as products_app

app = typer.Typer(cls=AliasTyperGroup, callback=show_banner)
app.add_typer(accounts_app, name="accounts")
app.add_typer(products_app, name="products")
app.add_typer(pricelists_app, name="pricelists")


try:
    VERSION = version("mpt-cli")
except PackageNotFoundError:  # pragma: no cover
    VERSION = "unknown"


__version__ = VERSION


def get_version():
    return __version__


def version_callback(value: bool):
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
    show_banner()


load_plugins(app)


if __name__ == "__main__":
    app()
