from typing import Any

from cli.core.console import console
from rich.table import Table


def flatten_dict(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    """Flatten a nested dictionary into a single level with dot notation keys."""
    items: list = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, v))
    return dict(items)


def format_json_path(path: str, source_trail: dict[str, Any], target_trail: dict[str, Any]) -> str:
    """Format JSON path with additional context from external IDs if available."""
    if not is_valid_path(path):
        return path

    array_path, _rest = path.split("]", 1)
    base_path, index_str = array_path.split("[")
    index = int(index_str)

    for trail in [source_trail, target_trail]:
        obj = trail
        for part in base_path.split("."):
            try:
                obj = obj[part]
            except KeyError:
                continue

        if (external_id := get_external_id(obj, index)) is not None:
            return f"{path} (externalId: {external_id})"

    return path


def is_valid_path(path: str) -> bool:
    """
    Check if a path is valid.

    Args:
        path: The path to check.

    Returns: True if the path is valid, False otherwise.

    """
    return "[" in path and "]" in path


def get_external_id(obj: Any, index: int) -> str | None:
    """
    Get the external ID from an object.

    Args:
        obj: the object to get the external ID from.
        index: the index of the object to get the external ID from.

    Returns: the external ID or None.

    """
    if isinstance(obj, list) and len(obj) > index:
        try:
            return obj[index]["externalId"]
        except (IndexError, KeyError):
            return None

    return None


def display_audit_records(records: list) -> None:
    """Display available audit records in a table format."""
    table = Table(title="Available Audit Records")
    table.add_column("Position", style="cyan", no_wrap=True)
    table.add_column("Timestamp", style="green", no_wrap=True)
    table.add_column("Audit ID", style="bright_blue")
    table.add_column("Actor", style="yellow")
    table.add_column("Event", style="magenta")
    table.add_column("Details", style="white")

    for idx, record in enumerate(records, 1):
        timestamp = record.get("timestamp", "N/A")
        audit_id = record.get("id", "N/A")
        actor = record.get("actor", {}).get("name", "N/A")
        actor_account = record.get("actor", {}).get("account", {}).get("name", "")
        if actor_account:
            actor = f"{actor} ({actor_account})"
        event = record.get("event", "N/A")
        details = record.get("details", "N/A")

        table.add_row(
            str(idx),
            timestamp,
            audit_id,
            actor,
            event.replace("platform.commerce.", ""),
            details,
        )

    console.print(table)
