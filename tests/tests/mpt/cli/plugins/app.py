import typer
from cli.core.console import console

app = typer.Typer()


@app.command()
def test():
    console.print("I'm a test plugin")


if __name__ == "__main__":
    app()
