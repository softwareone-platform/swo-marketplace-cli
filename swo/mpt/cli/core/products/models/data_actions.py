from enum import StrEnum


class DataActionEnum(StrEnum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    SKIP = "-"
