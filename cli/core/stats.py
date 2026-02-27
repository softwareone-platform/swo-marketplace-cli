import copy
from abc import ABC, abstractmethod
from typing import TypedDict

from rich import box
from rich.table import Table


class TabResults(TypedDict):
    """TypedDict representing the result statistics for synchronization operations.

    Attributes:
        synced: The number of successfully synchronized items.
        error: The number of items that encountered errors.
        total: The total number of processed items.
        skipped: The number of items that were skipped.

    """

    synced: int
    error: int
    total: int
    skipped: int


DEFAULT_RESULTS: TabResults = {
    "synced": 0,
    "error": 0,
    "total": 0,
    "skipped": 0,
}


class ErrorMessagesCollector:
    """Error messages collector."""

    def __init__(self) -> None:
        self._sections: dict[str, dict[str, list[str]]] = {}
        self._is_empty: bool = True

    def add_msg(self, section_name: str, item_name: str, msg: str) -> None:
        """Add an error message to a specific section and item.

        Args:
            section_name: The name of the section to add the message to.
            item_name: The name of the item within the section.
            msg: The error message to add.

        """
        self._is_empty = False

        if section_name not in self._sections:
            self._sections[section_name] = {}

        if item_name not in self._sections[section_name]:
            self._sections[section_name][item_name] = []

        self._sections[section_name][item_name].append(msg)

    def is_empty(self) -> bool:
        """Check if the collector has no error messages.

        Returns:
            True if no error messages have been added, False otherwise.

        """
        return self._is_empty

    def __str__(self) -> str:
        msg = ""
        for section_name, section in self._sections.items():
            msg = f"{msg}{section_name}:"
            section_messages = section.get("", [])
            if section_messages:
                msg = f"{msg} {', '.join(section_messages)}\n"
            else:
                msg += "\n"

            for item_name, item_messages in section.items():
                if not item_name:
                    continue

                msg = f"{msg}\t\t{item_name}: {', '.join(item_messages)}"

        return msg


class StatsCollector(ABC):
    """Abstract base class for collecting and managing operation statistics."""

    errors = ErrorMessagesCollector()

    def __init__(self, tabs: dict[str, TabResults]) -> None:
        self._stat_id: str | None = None
        self._has_error = False
        self._tab_aliases = tabs

    @property
    def stat_id(self) -> str | None:
        """Get the identifier of the stats collector.

        Returns:
            The identifier as a string, or None if not set.

        """
        return self._stat_id

    @stat_id.setter
    def stat_id(self, stat_value: str) -> None:
        self._stat_id = stat_value

    @property
    def tabs(self) -> dict[str, TabResults]:
        """Get the tab aliases with their results.

        Returns:
            A dictionary mapping tab names to their corresponding results.

        """
        return self._tab_aliases

    @property
    def has_errors(self) -> bool:
        """Check if any errors have been recorded."""
        return self._has_error

    def add_error(self, tab_name: str) -> None:
        """Increment error and total counters for a tab and mark errors as present.

        Args:
            tab_name: The name of the tab to update.

        """
        self._tab_aliases[tab_name]["error"] += 1
        self._tab_aliases[tab_name]["total"] += 1
        self._has_error = True

    def add_synced(self, tab_name: str) -> None:
        """Increment synced and total counters for a tab.

        Args:
            tab_name: The name of the tab to update.

        """
        self._tab_aliases[tab_name]["synced"] += 1
        self._tab_aliases[tab_name]["total"] += 1

    def add_skipped(self, tab_name: str) -> None:
        """Increment skipped and total counters for a tab.

        Args:
            tab_name: The name of the tab to update.

        """
        self._tab_aliases[tab_name]["skipped"] += 1
        self._tab_aliases[tab_name]["total"] += 1

    @abstractmethod
    def _get_table_title(self) -> str:
        raise NotImplementedError

    def to_table(self) -> Table:
        """Generate a rich Table representation of the collected stats.

        Returns:
            A Table object displaying the statistics for each tab.

        """
        table = Table(self._get_table_title(), box=box.ROUNDED)
        columns = ["Total", "Synced", "Errors", "Skipped"]
        for column in columns:
            table.add_column(column)

        for tab_name, tab_stats in self.tabs.items():
            table.add_row(
                tab_name,
                f"[blue]{tab_stats['total']}",
                f"[green]{tab_stats['synced']}",
                f"[red bold]{tab_stats['error']}",
                f"[white]{tab_stats['skipped']}",
            )
        return table


class ProductStatsCollector(StatsCollector):
    """Statistics collector specifically for product synchronization operations."""

    def __init__(self) -> None:
        general: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        parameters_groups: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        items_groups: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        agreements_parameters: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        asset_parameters: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        item_parameters: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        request_parameters: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        subscription_parameters: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        item_rows: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        templates: TabResults = copy.deepcopy(DEFAULT_RESULTS)

        tabs = {
            "General": general,
            "Parameters Groups": parameters_groups,
            "Items Groups": items_groups,
            "Agreements Parameters": agreements_parameters,
            "Assets Parameters": asset_parameters,
            "Item Parameters": item_parameters,
            "Request Parameters": request_parameters,
            "Subscription Parameters": subscription_parameters,
            "Items": item_rows,
            "Templates": templates,
        }

        super().__init__(tabs)

    def _get_table_title(self) -> str:
        status = "[red bold]FAILED" if self.has_errors else "[green bold]SUCCEED"
        return f"Product Sync {status}"


class PriceListStatsCollector(StatsCollector):
    """Statistics collector specifically for price list synchronization operations.

    This class tracks statistics for price list operations including
    general information and price items.
    """

    def __init__(self) -> None:
        general: TabResults = copy.deepcopy(DEFAULT_RESULTS)
        price_items: TabResults = copy.deepcopy(DEFAULT_RESULTS)

        tabs = {
            "General": general,
            "Price Items": price_items,
        }
        super().__init__(tabs)

    def _get_table_title(self) -> str:
        if self.has_errors:
            title = "Pricelist sync [red bold]FAILED"
        else:
            title = f"Pricelist {self.stat_id} sync [green bold]SUCCEED"

        return title
