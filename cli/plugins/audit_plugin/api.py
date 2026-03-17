from typing import Any

import typer
from cli.core.console import console
from mpt_api_client import RQLQuery

SELECT_FIELDS = ("object", "actor", "details", "documents", "request.api.geolocation")


def get_audit_trail(client: Any, record_id: str) -> dict[str, Any]:
    """Retrieve audit trail for a specific record."""
    # TODO: Using select instead of get because render() query string isn't working with get().
    audit_collection = client.audit.records.options(render=True)
    audit_collection_filtered = audit_collection.filter(RQLQuery(id=record_id))
    try:
        records = audit_collection_filtered.select(*SELECT_FIELDS).fetch_page(limit=1)
    except Exception as error:
        console.print(
            f"[red]Failed to retrieve audit trail for record {record_id}: {error!s}[/red]"
        )
        raise typer.Exit(1) from error

    if not records:
        console.print(f"[red]No audit record found with ID {record_id}[/red]")
        raise typer.Exit(1)

    return records[0].to_dict()


def get_audit_records_by_object(
    client: Any, object_id: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Retrieve all audit records for a specific object."""
    query = _records_query(client, object_id)
    try:
        raw_records = query.fetch_page(limit=limit)
    except Exception as error:
        console.print(
            f"[red]Failed to retrieve audit records for object {object_id}: {error!s}[/red]"
        )
        raise typer.Exit(1) from error

    records = [raw_record.to_dict() for raw_record in raw_records]
    if not records:
        console.print(f"[red]No audit records found for object {object_id}[/red]")
        raise typer.Exit(1)

    return records


def _records_query(client: Any, object_id: str) -> Any:
    object_id_filter = RQLQuery(object__id=object_id)
    return (
        client.audit.records
        .options(render=True)
        .filter(object_id_filter)
        .order_by("-timestamp")
        .select(*SELECT_FIELDS)
    )
