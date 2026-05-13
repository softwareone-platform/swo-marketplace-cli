from typing import Annotated, Any

import typer
from cli.core.accounts.app import get_active_account
from cli.core.console import console
from cli.core.console.renderers.audit import AuditDiffRenderer
from cli.core.mpt.mpt_client import create_api_mpt_client_from_account
from cli.plugins.audit_plugin.api import get_audit_records_by_object, get_audit_trail
from cli.plugins.audit_plugin.audit_records import (
    display_audit_records,
    flatten_dict,
    format_json_path,
)

app = typer.Typer(name="audit", help="Audit commands.")


class AuditTrailComparator:
    """Compare and render audit trail differences."""

    def __init__(self) -> None:
        self._renderer = AuditDiffRenderer()

    def compare(self, source_trail: dict[str, Any], target_trail: dict[str, Any]) -> None:
        """Compare two audit trails and display the differences."""
        self._check_same_object(source_trail, target_trail)

        console.print(
            self._renderer.render_summary(
                self._object_id(source_trail),
                source_trail.get("timestamp"),
                target_trail.get("timestamp"),
            )
        )

        differences = self._get_differences(source_trail, target_trail)
        if differences:
            console.print(self._renderer.render_differences(differences))
        else:
            console.print("\n[green]No differences found between the audit trails[/green]")

    def select_trails(
        self, records: list[dict[str, Any]], positions: str | None
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Select the two audit trails to compare from the loaded records."""
        if positions:
            try:
                parsed_positions = _parse_positions(positions, len(records))
            except ValueError:
                console.print(
                    "[red]Invalid positions. Please specify two numbers "
                    f"between 1 and {len(records)}[/red]"
                )
                raise typer.Exit(1)

            source_position, target_position = parsed_positions
            return records[source_position - 1], records[target_position - 1]

        console.print(
            "[yellow]No positions specified, comparing two most recent records (1,2)[/yellow]"
        )
        return records[0], records[1]

    def _check_same_object(
        self, source_trail: dict[str, Any], target_trail: dict[str, Any]
    ) -> None:
        if self._object_id(source_trail) == self._object_id(target_trail):
            return

        console.print("[red]Cannot compare different objects[/red]")
        raise typer.Exit(1)

    def _get_differences(
        self, source_trail: dict[str, Any], target_trail: dict[str, Any]
    ) -> list[tuple[str, str, str]]:
        source_flat = flatten_dict(source_trail)
        target_flat = flatten_dict(target_trail)
        return [
            (
                format_json_path(key, source_trail, target_trail),
                self._format_value(source_flat.get(key)),
                self._format_value(target_flat.get(key)),
            )
            for key in sorted(set(source_flat.keys()) | set(target_flat.keys()))
            if source_flat.get(key) != target_flat.get(key)
        ]

    def _format_value(self, audit_value: Any) -> str:
        if audit_value is None:
            return "[red]<missing>[/red]"

        return str(audit_value)

    def _object_id(self, audit_trail: dict[str, Any]) -> Any:
        return audit_trail.get("object", {}).get("id")


def compare_audit_trails(source_trail: dict[str, Any], target_trail: dict[str, Any]) -> None:
    """Compare two audit trails and display the differences."""
    AuditTrailComparator().compare(source_trail, target_trail)


def _parse_positions(positions: str, records_count: int) -> tuple[int, int]:
    pos1, pos2 = map(int, positions.split(","))
    if not (1 <= pos1 <= records_count and 1 <= pos2 <= records_count):
        raise ValueError
    return pos1, pos2


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

    source_trail, target_trail = AuditTrailComparator().select_trails(records, positions)
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


if __name__ == "__main__":
    main()
