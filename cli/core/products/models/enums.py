from enum import StrEnum


class DataActionEnum(StrEnum):
    """Enumeration of possible data actions for processing operations."""

    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    SKIP = "-"
    SKIPPED = ""


class ItemActionEnum(StrEnum):
    """Enumeration of possible item actions for item lifecycle management."""

    CREATE = "create"
    UPDATE = "update"
    REVIEW = "review"
    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
    SKIP = "-"
    SKIPPED = ""


class ItemTermsModelEnum(StrEnum):
    """Enumeration of item terms models for pricing structures."""

    ONE_TIME = "one-time"
    QUANTITY = "quantity"
    USAGE = "usage"
