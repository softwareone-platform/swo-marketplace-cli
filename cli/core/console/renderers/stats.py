from cli.core.stats import StatsCollector
from rich import box
from rich.table import Table


class StatsTableRenderer:
    """Render stats collectors as rich tables."""

    def render(self, stats: StatsCollector) -> Table:
        """Build the stats table for console output."""
        table = Table(stats.table_title(), box=box.ROUNDED)
        columns = ["", "Total", "Synced", "Errors", "Skipped"]
        for column in columns:
            table.add_column(column)

        for tab_name, tab_stats in stats.tabs.items():
            table.add_row(
                tab_name,
                f"[blue]{tab_stats['total']}",
                f"[green]{tab_stats['synced']}",
                f"[red bold]{tab_stats['error']}",
                f"[white]{tab_stats['skipped']}",
            )

        return table
