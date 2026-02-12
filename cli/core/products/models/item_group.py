import datetime as dt
from dataclasses import dataclass
from typing import Any, Self, override

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models.mixins import ActionMixin
from dateutil import parser


@dataclass
class ItemGroupData(BaseDataModel, ActionMixin):
    """Data model representing an item group."""

    id: str
    default: bool
    description: str
    display_order: int
    label: str
    multiple: bool
    name: str
    required: bool

    coordinate: str | None = None
    created_date: dt.date | None = None
    updated_date: dt.date | None = None

    @classmethod
    @override
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        return cls(
            id=row_data[constants.ITEMS_GROUPS_ID]["value"],
            coordinate=row_data[constants.ITEMS_GROUPS_ID]["coordinate"],
            name=row_data[constants.ITEMS_GROUPS_NAME]["value"],
            label=row_data[constants.ITEMS_GROUPS_LABEL]["value"],
            description=row_data[constants.ITEMS_GROUPS_DESCRIPTION]["value"],
            display_order=row_data[constants.ITEMS_GROUPS_DISPLAY_ORDER]["value"],
            default=row_data[constants.ITEMS_GROUPS_DEFAULT]["value"] == "True",
            multiple=row_data[constants.ITEMS_GROUPS_MULTIPLE_CHOICES]["value"] == "True",
            required=row_data[constants.ITEMS_GROUPS_REQUIRED]["value"] == "True",
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        updated = json_data["audit"].get("updated", {}).get("at")
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            label=json_data["label"],
            description=json_data["description"],
            display_order=json_data["displayOrder"],
            default=json_data["default"],
            multiple=json_data["multiple"],
            required=json_data["required"],
            created_date=parser.parse(json_data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "displayOrder": self.display_order,
            "default": self.default,
            "multiple": self.multiple,
            "required": self.required,
        }

    @override
    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.ITEMS_GROUPS_ID: self.id,
            constants.ITEMS_GROUPS_NAME: self.name,
            constants.ITEMS_GROUPS_ACTION: self.action,
            constants.ITEMS_GROUPS_LABEL: self.label,
            constants.ITEMS_GROUPS_DISPLAY_ORDER: self.display_order,
            constants.ITEMS_GROUPS_DESCRIPTION: self.description,
            constants.ITEMS_GROUPS_DEFAULT: str(self.default),
            constants.ITEMS_GROUPS_MULTIPLE_CHOICES: str(self.multiple),
            constants.ITEMS_GROUPS_REQUIRED: str(self.required),
            constants.ITEMS_GROUPS_CREATED: self.created_date,
            constants.ITEMS_GROUPS_MODIFIED: self.updated_date,
        }
