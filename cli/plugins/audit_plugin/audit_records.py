from typing import Any

from cli.core.console import console
from rich.table import Table

TrailData = dict[str, Any]
type FlatItems = list[tuple[str, Any]]


def flatten_dict(
    source_dict: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """Flatten a nested dictionary into a single level with dot notation keys."""
    flattened_items: FlatItems = []
    for key, node_value in source_dict.items():
        flattened_items.extend(_AuditRecordsOps.flatten_items(key, node_value, parent_key, sep))
    return dict(flattened_items)


def format_json_path(path: str, source_trail: TrailData, target_trail: TrailData) -> str:
    """Format JSON path with additional context from external IDs if available."""
    if not is_valid_path(path):
        return path

    base_path, index = _AuditRecordsOps.path_details(path)

    for trail in [source_trail, target_trail]:
        current_node = _AuditRecordsOps.resolve_current_node(trail, base_path)

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
        _AuditRecordsOps.add_record_row(table, idx, record)

    console.print(table)


class _AuditRecordsOps:
    @classmethod
    def add_record_row(cls, table: Table, index: int, record: dict[str, Any]) -> None:
        actor_data = record.get("actor", {})
        actor_name = actor_data.get("name", "N/A")
        actor_account = actor_data.get("account", {}).get("name", "")
        actor = actor_name
        if actor_account:
            actor = f"{actor_name} ({actor_account})"
        table.add_row(
            str(index),
            record.get("timestamp", "N/A"),
            record.get("id", "N/A"),
            actor,
            record.get("event", "N/A").replace("platform.commerce.", ""),
            record.get("details", "N/A"),
        )

    @classmethod
    def flatten_items(cls, key: str, node_value: Any, parent_key: str, sep: str) -> FlatItems:
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(node_value, dict):
            return list(flatten_dict(node_value, new_key, sep=sep).items())
        if isinstance(node_value, list):
            return cls.flatten_list_items(node_value, new_key, sep)
        return [(new_key, node_value)]

    @classmethod
    def flatten_list_items(cls, node_value: list[Any], new_key: str, sep: str) -> FlatItems:
        flattened_items: FlatItems = []
        for index, list_entry in enumerate(node_value):
            list_key = f"{new_key}[{index}]"
            if isinstance(list_entry, dict):
                flattened_items.extend(flatten_dict(list_entry, list_key, sep=sep).items())
            else:
                flattened_items.append((list_key, list_entry))
        return flattened_items

    @classmethod
    def path_details(cls, path: str) -> tuple[str, int]:
        array_path, _rest = path.split("]", 1)
        base_path, index_str = array_path.split("[")
        return base_path, int(index_str)

    @classmethod
    def resolve_current_node(cls, trail: TrailData, base_path: str) -> Any:
        current_node: Any = trail
        for part in base_path.split("."):
            if not isinstance(current_node, dict):
                return {}
            current_node = current_node.get(part, {})
        return current_node
