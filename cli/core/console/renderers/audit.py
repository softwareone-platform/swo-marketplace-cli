from typing import Any

from rich import box
from rich.panel import Panel
from rich.table import Table


class AuditRecordsRenderer:
    """Render audit record collections."""

    def render(self, records: list[dict[str, Any]]) -> Table:
        """Build the audit-record list table."""
        table = Table(title="Available Audit Records", box=box.ROUNDED)
        table.add_column("Position", style="cyan", no_wrap=True)
        table.add_column("Timestamp", style="green", no_wrap=True)
        table.add_column("Audit ID", style="bright_blue")
        table.add_column("Actor", style="yellow")
        table.add_column("Event", style="magenta")
        table.add_column("Details", style="white")

        for idx, record in enumerate(records, 1):
            table.add_row(
                str(idx),
                record.get("timestamp", "N/A"),
                record.get("id", "N/A"),
                self._get_actor(record),
                record.get("event", "N/A").replace("platform.commerce.", ""),
                record.get("details", "N/A"),
            )

        return table

    def _get_actor(self, record: dict[str, Any]) -> str:
        actor = record.get("actor") or {}
        actor_name = actor.get("name", "N/A")
        actor_account = actor.get("account", {}).get("name", "")
        if actor_account:
            actor_name = f"{actor_name} ({actor_account})"

        return actor_name


class AuditDiffRenderer:
    """Render audit comparison summaries and differences."""

    def render_summary(
        self, object_id: str | None, source_timestamp: str | None, target_timestamp: str | None
    ) -> Panel:
        """Build the audit comparison summary panel."""
        return Panel(
            f"Comparing audit trails...\n"
            f"Object ID: {object_id}\n"
            f"Source Timestamp: {source_timestamp}\n"
            f"Target Timestamp: {target_timestamp}"
        )

    def render_differences(
        self, differences: list[tuple[str, str, str]], *, title: str = "Audit Trail Differences"
    ) -> Table:
        """Build the audit differences table."""
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Path", style="cyan")
        table.add_column("Source Value", style="green")
        table.add_column("Target Value", style="yellow")

        for path, source_value, target_value in differences:
            table.add_row(path, source_value, target_value)

        return table
