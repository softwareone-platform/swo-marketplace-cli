from typing import Any

from cli.core.console import console
from rich.table import Table


def flatten_dict(
    source_dict: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """Flatten a nested dictionary into a single level with dot notation keys."""
    flattened_items: list = []
    for key, node_value in source_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(node_value, dict):
            flattened_items.extend(flatten_dict(node_value, new_key, sep=sep).items())
        elif isinstance(node_value, list):
            for index, list_entry in enumerate(node_value):
                if isinstance(list_entry, dict):
                    flattened_items.extend(
                        flatten_dict(list_entry, f"{new_key}[{index}]", sep=sep).items()
                    )
                else:
                    flattened_items.append((f"{new_key}[{index}]", list_entry))
        else:
            flattened_items.append((new_key, node_value))
    return dict(flattened_items)


def format_json_path(path: str, source_trail: dict, target_trail: dict) -> str:
    """Format JSON path with additional context from external IDs if available."""
    if not is_valid_path(path):
        return path

    array_path, _rest = path.split("]", 1)
    base_path, index_str = array_path.split("[")
    index = int(index_str)

    for trail in [source_trail, target_trail]:
        current_node = trail
        for part in base_path.split("."):
            try:
                current_node = current_node[part]
            except KeyError:
                continue

        if (external_id := get_external_id(current_node, index)) is not None:
            return f"{path} (externalId: {external_id})"

    return path


def is_valid_path(path: str) -> bool:
    """Check if a path is valid.

    Args:
        path: The path to check.

    Returns: True if the path is valid, False otherwise.

    """
    return "[" in path and "]" in path


def get_external_id(current_node: Any, index: int) -> str | None:
    """Get the external ID from an object.

    Args:
        current_node: the object to get the external ID from.
        index: the index of the object to get the external ID from.

    Returns: the external ID or None.

    """
    if isinstance(current_node, list) and len(current_node) > index:
        try:
            return current_node[index]["externalId"]
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
        actor_data = record.get("actor", {})
        actor = actor_data.get("name", "N/A")
        actor_account = actor_data.get("account", {}).get("name", "")
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
