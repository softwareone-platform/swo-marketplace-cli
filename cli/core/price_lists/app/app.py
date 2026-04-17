import typer
from cli.core.price_lists.app.export import app as export_app
from cli.core.price_lists.app.sync import app as sync_app

app = typer.Typer()
app.add_typer(export_app)
app.add_typer(sync_app)

if __name__ == "__main__":
    app()
