from typing import Any, Dict, Optional

import typer
from rich.panel import Panel
from rich.table import Table
from swo.mpt.cli.core.accounts.app import get_active_account
from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.mpt.client import client_from_account

from .api import get_audit_records_by_object, get_audit_trail
from .utils import display_audit_records, flatten_dict, format_json_path

app = typer.Typer(name="audit", help="Audit commands.")


def compare_audit_trails(source_trail: Dict[str, Any], target_trail: Dict[str, Any]) -> None:
    """Compare two audit trails and display the differences."""
    # Ensure we're comparing the same object
    source_object_id = source_trail.get('object', {}).get('id')
    target_object_id = target_trail.get('object', {}).get('id')

    if source_object_id != target_object_id:
        console.print("[red]Cannot compare different objects[/red]")
        raise typer.Exit(1)

    # Create panel with basic information
    panel = Panel(
        f"Comparing audit trails...\n"
        f"Object ID: {source_object_id}\n"
        f"Source Timestamp: {source_trail.get('timestamp')}\n"
        f"Target Timestamp: {target_trail.get('timestamp')}"
    )
    console.print(panel)

    # Flatten both dictionaries for comparison
    source_flat = flatten_dict(source_trail)
    target_flat = flatten_dict(target_trail)

    # Create sets of all keys
    all_keys = set(source_flat.keys()) | set(target_flat.keys())

    # Create table for differences
    table = Table(title="Audit Trail Differences")
    table.add_column("Path", style="cyan")
    table.add_column("Source Value", style="green")
    table.add_column("Target Value", style="yellow")

    differences_found = False

    for key in sorted(all_keys):
        source_value = source_flat.get(key)
        target_value = target_flat.get(key)

        if source_value != target_value:
            differences_found = True
            formatted_path = format_json_path(key, source_trail, target_trail)
            table.add_row(
                formatted_path,
                str(source_value) if source_value is not None else "[red]<missing>[/red]",
                str(target_value) if target_value is not None else "[red]<missing>[/red]"
            )

    if differences_found:
        console.print(table)
    else:
        console.print("\n[green]No differences found between the audit trails[/green]")


@app.command()
def diff_by_object_id(
    object_id: str = typer.Argument(
        ...,
        help="Object ID to fetch and compare all audit records for"
    ),
    positions: Optional[str] = typer.Option(
        None,
        "--positions",
        help="Positions to compare (e.g. '1,3')"
    ),
    limit: int = typer.Option(10, "--limit", help="Maximum number of audit records to retrieve")
):
    """Compare audit trails for a specific object."""
    account = get_active_account()
    client = client_from_account(account)

    records = get_audit_records_by_object(client, object_id, limit)
    if len(records) < 2:
        console.print("[red]Need at least 2 audit records to compare[/red]")
        raise typer.Exit(1)

    display_audit_records(records)

    if positions:
        try:
            pos1, pos2 = map(int, positions.split(','))
            if not (1 <= pos1 <= len(records) and 1 <= pos2 <= len(records)):
                raise ValueError
        except ValueError:
            msg = (
                "[red]Invalid positions. Please specify two numbers "
                f"between 1 and {len(records)}[/red]"
            )
            console.print(msg)
            raise typer.Exit(1)

        source_trail = records[pos1 - 1]
        target_trail = records[pos2 - 1]
    else:
        source_trail = records[0]
        target_trail = records[1]
        console.print(
            "[yellow]No positions specified, comparing two most recent records (1,2)[/yellow]"
        )

    compare_audit_trails(source_trail, target_trail)


@app.command()
def diff_by_records_id(
    source: str = typer.Argument(..., help="ID of the source audit record"),
    target: str = typer.Argument(..., help="ID of the target audit record")
):
    """Compare audit trails between two specific audit record IDs."""
    account = get_active_account()
    client = client_from_account(account)

    source_trail = get_audit_trail(client, source)
    target_trail = get_audit_trail(client, target)

    compare_audit_trails(source_trail, target_trail)


def main():  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
