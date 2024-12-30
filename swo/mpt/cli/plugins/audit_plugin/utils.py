from typing import Any, Dict

from rich.table import Table
from swo.mpt.cli.core.console import console


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
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


def format_json_path(path: str, source_trail: Dict[str, Any], target_trail: Dict[str, Any]) -> str:
    """Format JSON path with additional context from external IDs if available."""
    if '[' in path and ']' in path:
        array_path, rest = path.split(']', 1)
        base_path, index_str = array_path.split('[')
        index = int(index_str)

        for trail in [source_trail, target_trail]:
            try:
                obj = trail
                for part in base_path.split('.'):
                    obj = obj[part]
                if isinstance(obj, list) and len(obj) > index:
                    if 'externalId' in obj[index]:
                        return f"{path} (externalId: {obj[index]['externalId']})"
            except (KeyError, IndexError, TypeError):
                continue

    return path


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
        timestamp = record.get('timestamp', 'N/A')
        audit_id = record.get('id', 'N/A')
        actor = record.get('actor', {}).get('name', 'N/A')
        actor_account = record.get('actor', {}).get('account', {}).get('name', '')
        if actor_account:
            actor = f"{actor} ({actor_account})"
        event = record.get('event', 'N/A')
        details = record.get('details', 'N/A')

        table.add_row(
            str(idx),
            timestamp,
            audit_id,
            actor,
            event.replace('platform.commerce.', ''),
            details
        )

    console.print(table)
