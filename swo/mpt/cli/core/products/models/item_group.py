from dataclasses import dataclass
from datetime import date
from typing import Any, Self

from dateutil import parser
from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.products.models.data_actions import DataAction


@dataclass
class ItemGroupData(BaseDataModel):
    id: str
    default: bool
    description: str
    display_order: str
    label: str
    multiple: bool
    name: str
    required: bool

    action: DataAction = DataAction.SKIP
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
        return cls(
            id=data["id"],
            coordinate=data[constants.ITEMS_GROUPS_ID]["coordinate"],
            name=data[constants.ITEMS_GROUPS_NAME]["value"],
            label=data[constants.ITEMS_GROUPS_LABEL]["value"],
            description=data[constants.ITEMS_GROUPS_DESCRIPTION]["value"],
            display_order=data[constants.ITEMS_GROUPS_DISPLAY_ORDER]["value"],
            default=data[constants.ITEMS_GROUPS_DEFAULT]["value"] == "True",
            multiple=data[constants.ITEMS_GROUPS_MULTIPLE_CHOICES]["value"] == "True",
            required=data[constants.ITEMS_GROUPS_REQUIRED]["value"] == "True",
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=parser.parse(data["audit"]["updated"]["at"]).date(),
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
            constants.ITEMS_GROUPS_DEFAULT: self.default,
            constants.ITEMS_GROUPS_MULTIPLE_CHOICES: self.multiple,
            constants.ITEMS_GROUPS_REQUIRED: self.required,
            constants.ITEMS_GROUPS_CREATED: self.created_date,
            constants.ITEMS_GROUPS_MODIFIED: self.updated_date,
        }
