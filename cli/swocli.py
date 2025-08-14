import logging
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Annotated

import typer
from cli.core.accounts import app as accounts_app
from cli.core.alias_group import AliasTyperGroup
from cli.core.console import console, show_banner
from cli.core.plugins import load_plugins
from cli.core.price_lists import app as price_lists_app
from cli.core.products import app as products_app
from cli.core.state import state

app = typer.Typer(cls=AliasTyperGroup, callback=show_banner)
app.add_typer(accounts_app, name="accounts")
app.add_typer(products_app, name="products")
app.add_typer(price_lists_app, name="pricelists")


try:
    VERSION = version("mpt-cli")
except PackageNotFoundError:  # pragma: no cover
    VERSION = "unknown"


__version__ = VERSION


def get_version() -> str:
    """Get the current CLI version."""
    return __version__


def version_callback(value: bool) -> None:  # noqa: FBT001
    """Callback to display the CLI version and exit if requested.

    Args:
        value: If True, prints the version and exits.

    """
    if value:
        console.print(f"version: {get_version()}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
    verbose: Annotated[  # noqa: FBT002
        bool,
        typer.Option(
            "--verbose",
            help="Enable verbose mode with console output",
            is_flag=True,
        ),
    ] = False,
    log_file: Annotated[
        Path | None,
        typer.Option(
            "--log-file",
            help="File path for debug logs (disables console output)",
            dir_okay=False,
        ),
    ] = None,
) -> None:
    """Main callback for the CLI application.

    Args:
        version: If True, displays the CLI version and exits.
        verbose: Enables verbose mode with console output.
        log_file: File path for debug logs, disables console output if set.

    """
    if verbose and log_file:
        console.print("[red]Error: Cannot use both --verbose and --log-file together[/]")
        raise typer.Exit(1)

    if verbose or log_file:
        if log_file:
            # Create parent directories if they don't exist
            log_file.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_file)
            console.print(f"Debug logs will be written to: {log_file}")
        else:
            handler = logging.StreamHandler()  # type: ignore[assignment]

        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(name)s:\n%(message)s\n",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[handler],
        )
        state.verbose = True
    show_banner()


load_plugins(app)


if __name__ == "__main__":
    app()
