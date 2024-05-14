import copy
from typing import TypedDict


class Results(TypedDict):
    synced: int
    error: int
    total: int
    skipped: int


DEFAULT_RESULTS: Results = {
    "synced": 0,
    "error": 0,
    "total": 0,
    "skipped": 0,
}


class ErrorMessagesCollector:
    """
    Error messages collector
    """

    def __init__(self) -> None:
        self._sections: dict[str, dict[str, list[str]]] = {}
        self._is_empty: bool = True

    def add_msg(self, section_name: str, item_name: str, msg: str):
        self._is_empty = False

        if section_name not in self._sections:
            self._sections[section_name] = {}

        if item_name not in self._sections[section_name]:
            self._sections[section_name][item_name] = []

        self._sections[section_name][item_name].append(msg)

    def is_empty(self) -> bool:
        return self._is_empty

    def __str__(self) -> str:
        msg = ""

        for section_name, section in self._sections.items():
            msg = f"{msg}{section_name}:"
            if "" in section:
                msg = f"{msg} {', '.join(section[''])}\n"
            else:
                msg += "\n"

            for item_name, item_messages in section.items():
                if item_name == "":
                    continue

                msg = f"{msg}\t\t{item_name}: {', '.join(item_messages)}"

        return msg


class ProductStatsCollector:
    def __init__(self) -> None:
        self.general: Results = copy.deepcopy(DEFAULT_RESULTS)
        self.parameters_groups: Results = copy.deepcopy(DEFAULT_RESULTS)
        self.items_groups: Results = copy.deepcopy(DEFAULT_RESULTS)
        self.agreements_parameters: Results = copy.deepcopy(DEFAULT_RESULTS)
        self.item_parameters: Results = copy.deepcopy(DEFAULT_RESULTS)
        self.request_parameters: Results = copy.deepcopy(DEFAULT_RESULTS)
        self.subscription_parameters: Results = copy.deepcopy(DEFAULT_RESULTS)
        self.items: Results = copy.deepcopy(DEFAULT_RESULTS)
        self.templates: Results = copy.deepcopy(DEFAULT_RESULTS)

        self.__has_error = False

        self.__tab_aliases = {
            "General": self.general,
            "Parameters Groups": self.parameters_groups,
            "Items Groups": self.items_groups,
            "Agreements Parameters": self.agreements_parameters,
            "Item Parameters": self.item_parameters,
            "Request Parameters": self.request_parameters,
            "Subscription Parameters": self.subscription_parameters,
            "Items": self.items,
            "Templates": self.templates,
        }

    def add_error(self, tab_name: str) -> None:
        self.__tab_aliases[tab_name]["error"] += 1
        self.__tab_aliases[tab_name]["total"] += 1
        self.__has_error = True

    def add_synced(self, tab_name: str) -> None:
        self.__tab_aliases[tab_name]["synced"] += 1
        self.__tab_aliases[tab_name]["total"] += 1

    def add_skipped(self, tab_name: str) -> None:
        self.__tab_aliases[tab_name]["skipped"] += 1
        self.__tab_aliases[tab_name]["total"] += 1

    @property
    def tabs(self) -> dict[str, Results]:
        return self.__tab_aliases

    @property
    def is_error(self) -> bool:
        return self.__has_error
