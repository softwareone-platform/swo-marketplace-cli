from typing import Any

import typer
from cli.core.console import console
from mpt_api_client import MPTClient, RQLQuery


def get_audit_trail(client: MPTClient, record_id: str) -> dict[str, Any]:
    """Retrieve audit trail for a specific record."""
    try:
        # TODO: Using select instead of get because render() query string isn't working with get().
        select_fields = ["object", "actor", "details", "documents", "request.api.geolocation"]
        audit_collection = client.audit.records.options(render=True)  # type: ignore[attr-defined]
        audit_collection_filtered = audit_collection.filter(RQLQuery(id=record_id))
        records = audit_collection_filtered.select(*select_fields).fetch_page(limit=1)
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
    try:
        select_fields = ["object", "actor", "details", "documents", "request.api.geolocation"]
        object_id_filter = RQLQuery(object__id=object_id)
        order_by = "-timestamp"
        audit_records_collection = client.audit.records.options(render=True)
        audit_records_filtered = audit_records_collection.filter(object_id_filter)
        raw_records = (
            audit_records_filtered.order_by(order_by).select(*select_fields).fetch_page(limit=limit)
        )
        records = [raw_record.to_dict() for raw_record in raw_records]
    except Exception as error:
        console.print(
            f"[red]Failed to retrieve audit records for object {object_id}: {error!s}[/red]"
        )
        raise typer.Exit(1) from error

    if not records:
        console.print(f"[red]No audit records found for object {object_id}[/red]")
        raise typer.Exit(1)

    return records
