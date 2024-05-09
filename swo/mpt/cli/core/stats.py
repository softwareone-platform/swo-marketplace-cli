from typing import TypeAlias

RowError: TypeAlias = tuple[str, str]


class StatsCollector:
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
        self.general: list[RowError] = []

        self.__tab_aliases = {
            "general": self.general,
        }

        self._is_empty = True

    def add_error(self, tab_alias: str, error: RowError) -> None:
        errors = self.__tab_aliases[tab_alias]
        errors.append(error)

    def is_empty(self) -> bool:
        return self._is_empty
