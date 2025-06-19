from enum import StrEnum


class DataAction(StrEnum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    SKIP = "-"
