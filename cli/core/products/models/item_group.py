from dataclasses import dataclass
from datetime import date
from typing import Any, Self

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models.mixins import ActionMixin
from dateutil import parser


@dataclass
class ItemGroupData(BaseDataModel, ActionMixin):
    id: str
    default: bool
    description: str
    display_order: int
    label: str
    multiple: bool
    name: str
    required: bool

    coordinate: str | None = None
    created_date: date | None = None
    updated_date: date | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data[constants.ITEMS_GROUPS_ID]["value"],
            coordinate=data[constants.ITEMS_GROUPS_ID]["coordinate"],
            name=data[constants.ITEMS_GROUPS_NAME]["value"],
            label=data[constants.ITEMS_GROUPS_LABEL]["value"],
            description=data[constants.ITEMS_GROUPS_DESCRIPTION]["value"],
            display_order=data[constants.ITEMS_GROUPS_DISPLAY_ORDER]["value"],
            default=data[constants.ITEMS_GROUPS_DEFAULT]["value"] == "True",
            multiple=data[constants.ITEMS_GROUPS_MULTIPLE_CHOICES]["value"] == "True",
            required=data[constants.ITEMS_GROUPS_REQUIRED]["value"] == "True",
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        updated = data["audit"].get("updated", {}).get("at")
        return cls(
            id=data["id"],
            name=data["name"],
            label=data["label"],
            description=data["description"],
            display_order=data["displayOrder"],
            default=data["default"],
            multiple=data["multiple"],
            required=data["required"],
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=updated and parser.parse(updated).date() or None,
        )

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
