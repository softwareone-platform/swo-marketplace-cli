from typing import Annotated, Any

import typer
from cli.core.accounts.app import get_active_account
from cli.core.console import console
from cli.core.mpt.mpt_client import create_api_mpt_client_from_account
from cli.plugins.audit_plugin.api import get_audit_records_by_object, get_audit_trail
from cli.plugins.audit_plugin.audit_records import (
    display_audit_records,
    flatten_dict,
    format_json_path,
)
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(name="audit", help="Audit commands.")
type TrailData = dict[str, Any]
type TrailValues = dict[str, Any]


def compare_audit_trails(source_trail: TrailData, target_trail: TrailData) -> None:
    """Compare two audit trails and display the differences. Prints the differences to the console.

    Args:
        source_trail: The source audit trail as a dictionary.
        target_trail: The target audit trail as a dictionary.

    """
    source_object_id = _AuditDiffOps.object_id(source_trail)
    if source_object_id != _AuditDiffOps.object_id(target_trail):
        console.print("[red]Cannot compare different objects[/red]")
        raise typer.Exit(1)

    _AuditDiffOps.print_compare_panel(source_object_id, source_trail, target_trail)
    table = _AuditDiffOps.comparison_table(source_trail, target_trail)
    if table is None:
        console.print("\n[green]No differences found between the audit trails[/green]")
    else:
        console.print(table)


@app.command()
def diff_by_object_id(
    object_id: Annotated[
        str,
        typer.Argument(..., help="Object ID to fetch and compare all audit records for"),
    ],
    positions: Annotated[
        str | None,
        typer.Option("--positions", help="Positions to compare (e.g. '1,3')"),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", help="Maximum number of audit records to retrieve"),
    ] = 10,
) -> None:
    """Compare audit trails for a specific object. Prints the comparison result to the console.

    Args:
        object_id: The object ID to fetch audit records for.
        positions: The positions of records to compare, as a comma-separated string.
        limit: The maximum number of audit records to retrieve.

    """
    account = get_active_account()
    client = create_api_mpt_client_from_account(account)

    records = get_audit_records_by_object(client, object_id, limit)
    if len(records) < 2:
        console.print("[red]Need at least 2 audit records to compare[/red]")
        raise typer.Exit(1)

    display_audit_records(records)
    source_trail, target_trail = _AuditDiffOps.select_records(records, positions)
    compare_audit_trails(source_trail, target_trail)


@app.command()
def diff_by_records_id(
    source: Annotated[str, typer.Argument(..., help="ID of the source audit record")],
    target: Annotated[str, typer.Argument(..., help="ID of the target audit record")],
) -> None:
    """Compare audit trails between two specific audit record IDs.

    Args:
        source: The ID of the source audit record.
        target: The ID of the target audit record.

    """
    account = get_active_account()
    client = create_api_mpt_client_from_account(account)

    source_trail = get_audit_trail(client, source)
    target_trail = get_audit_trail(client, target)

    compare_audit_trails(source_trail, target_trail)


def main() -> None:  # pragma: no cover
    """Entry point for the audit CLI application."""
    app()


class _AuditDiffOps:
    @classmethod
    def comparison_row(
        cls,
        key: str,
        source_value: Any,
        target_value: Any,
        source_trail: TrailData,
        target_trail: TrailData,
    ) -> tuple[str, str, str]:
        return (
            format_json_path(key, source_trail, target_trail),
            "[red]<missing>[/red]" if source_value is None else str(source_value),
            "[red]<missing>[/red]" if target_value is None else str(target_value),
        )

    @classmethod
    def comparison_rows(
        cls,
        source_trail: TrailData,
        target_trail: TrailData,
    ) -> list[tuple[str, str, str]]:
        source_flat = flatten_dict(source_trail)
        target_flat = flatten_dict(target_trail)
        return [
            cls.comparison_row(
                key, source_flat.get(key), target_flat.get(key), source_trail, target_trail
            )
            for key in cls.sorted_keys(source_flat, target_flat)
            if source_flat.get(key) != target_flat.get(key)
        ]

    @classmethod
    def comparison_table(cls, source_trail: TrailData, target_trail: TrailData) -> Table | None:
        table = Table(title="Audit Trail Differences")
        table.add_column("Path", style="cyan")
        table.add_column("Source Value", style="green")
        table.add_column("Target Value", style="yellow")

        rows = cls.comparison_rows(source_trail, target_trail)
        if not rows:
            return None
        for row in rows:
            table.add_row(*row)
        return table

    @classmethod
    def object_id(cls, trail: TrailData) -> str | None:
        return trail.get("object", {}).get("id")

    @classmethod
    def parse_positions(cls, positions: str, records_len: int) -> tuple[int, int]:
        pos1, pos2 = map(int, positions.split(","))
        first_position_valid = 1 <= pos1 <= records_len
        second_position_valid = 1 <= pos2 <= records_len
        if not (first_position_valid and second_position_valid):
            raise ValueError
        return pos1, pos2

    @classmethod
    def print_compare_panel(
        cls,
        source_object_id: str | None,
        source_trail: TrailData,
        target_trail: TrailData,
    ) -> None:
        console.print(
            Panel(
                f"Comparing audit trails...\n"
                f"Object ID: {source_object_id}\n"
                f"Source Timestamp: {source_trail.get('timestamp')}\n"
                f"Target Timestamp: {target_trail.get('timestamp')}"
            )
        )

    @classmethod
    def select_records(
        cls, records: list[TrailData], positions: str | None
    ) -> tuple[TrailData, TrailData]:
        if positions is None:
            console.print(
                "[yellow]No positions specified, comparing two most recent records (1,2)[/yellow]"
            )
            return records[0], records[1]
        try:
            pos1, pos2 = cls.parse_positions(positions, len(records))
        except ValueError:
            console.print(
                "[red]Invalid positions. Please specify two numbers "
                f"between 1 and {len(records)}[/red]"
            )
            raise typer.Exit(1)
        return records[pos1 - 1], records[pos2 - 1]

    @classmethod
    def sorted_keys(cls, source_flat: TrailValues, target_flat: TrailValues) -> list[str]:
        all_keys = set(source_flat.keys())
        all_keys.update(target_flat.keys())
        return sorted(all_keys)


if __name__ == "__main__":
    main()
