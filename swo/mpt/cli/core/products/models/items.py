from dataclasses import dataclass
from typing import Any

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants


@dataclass
class ItemGroupData(BaseDataModel):
    id: str
    coordinate: str
    name: str
    label: str
    description: str
    display_order: str
    default: str
    multiple: bool
    required: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ItemGroupData":
        return cls(
            id=data[constants.ITEMS_GROUPS_ID]["value"],
            coordinate=data[constants.ITEMS_GROUPS_ID]["coordinate"],
            name=data[constants.ITEMS_GROUPS_NAME]["value"],
            label=data[constants.ITEMS_GROUPS_LABEL]["value"],
            description=data[constants.ITEMS_GROUPS_DESCRIPTION]["value"],
            display_order=data[constants.ITEMS_GROUPS_DISPLAY_ORDER]["value"],
            default=data[constants.ITEMS_GROUPS_DEFAULT]["value"],
            multiple=data[constants.ITEMS_GROUPS_MULTIPLE_CHOICES]["value"] == "True",
            required=data[constants.ITEMS_GROUPS_REQUIRED]["value"] == "True"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "coordinate": self.coordinate,
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "displayOrder": self.display_order,
            "default": self.default,
            "multiple": self.multiple,
            "required": self.required,
        }