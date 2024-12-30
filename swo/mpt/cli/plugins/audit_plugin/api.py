from typing import Any, Dict, List

import typer
from swo.mpt.cli.core.console import console


def get_audit_trail(client: Any, record_id: str) -> Dict[str, Any]:
    """Retrieve audit trail for a specific record."""
    try:
        endpoint = f"/audit/records/{record_id}"
        params = (
            "render()&select=object,actor,details,documents,request.api.geolocation"
        )
        response = client.get(endpoint + "?" + params)
        return response.json()
    except Exception as e:
        console.print(f"[red]Failed to retrieve audit trail for record {record_id}: {str(e)}[/red]")
        raise typer.Exit(1)


def get_audit_records_by_object(
    client: Any,
    object_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Retrieve all audit records for a specific object."""
    try:
        endpoint = "/audit/records"
        params = (
            "render()&select=object,actor,details,documents,request.api.geolocation"
            f"&eq(object.id,{object_id})&order=-timestamp&limit={limit}"
        )
        response = client.get(endpoint + "?" + params)
        records = response.json().get('data', [])
        if not records:
            console.print(f"[red]No audit records found for object {object_id}[/red]")
            raise typer.Exit(1)
        return records
    except Exception as e:
        console.print(
            f"[red]Failed to retrieve audit records for object {object_id}: {str(e)}[/red]"
        )
        raise typer.Exit(1)
