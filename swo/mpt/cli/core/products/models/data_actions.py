from enum import StrEnum


class DataActionEnum(StrEnum):
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    SKIP = "-"
    SKIPPED = ""


class ItemActionEnum(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    REVIEW = "review"
    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
    SKIP = "-"
    SKIPPED = ""
