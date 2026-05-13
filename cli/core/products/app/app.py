import typer
from cli.core.products.app.export import app as export_app
from cli.core.products.app.list_products import app as list_app
from cli.core.products.app.sync import app as sync_app

app = typer.Typer()
app.add_typer(export_app)
app.add_typer(list_app)
app.add_typer(sync_app)

if __name__ == "__main__":
    app()
