from dataclasses import dataclass
from datetime import date
from typing import Any, Self

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models.mixins import ActionMixin
from dateutil import parser


@dataclass
class ParameterGroupData(BaseDataModel, ActionMixin):
    id: str
    default: bool
    description: str
    display_order: int
    label: str
    name: str

    coordinate: str | None = None
    created_date: date | None = None
    updated_date: date | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data[constants.PARAMETERS_GROUPS_ID]["value"],
            coordinate=data[constants.PARAMETERS_GROUPS_ID]["coordinate"],
            default=data[constants.PARAMETERS_GROUPS_DEFAULT]["value"] == "True",
            description=data[constants.PARAMETERS_GROUPS_DESCRIPTION]["value"],
            display_order=int(data[constants.PARAMETERS_GROUPS_DISPLAY_ORDER]["value"]),
            label=data[constants.PARAMETERS_GROUPS_LABEL]["value"],
            name=data[constants.PARAMETERS_GROUPS_NAME]["value"],
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        updated = data["audit"].get("updated", {}).get("at")
        return cls(
            id=data["id"],
            description=data["description"],
            default=data["default"],
            display_order=data["displayOrder"],
            label=data["label"],
            name=data["name"],
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=updated and parser.parse(updated).date() or None,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "default": self.default,
            "description": self.description,
            "displayOrder": self.display_order,
            "label": self.label,
            "name": self.name,
        }

    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.PARAMETERS_GROUPS_ID: self.id,
            constants.PARAMETERS_GROUPS_NAME: self.name,
            constants.PARAMETERS_GROUPS_ACTION: self.action,
            constants.PARAMETERS_GROUPS_LABEL: self.label,
            constants.PARAMETERS_GROUPS_DISPLAY_ORDER: self.display_order,
            constants.PARAMETERS_GROUPS_DESCRIPTION: self.description,
            constants.PARAMETERS_GROUPS_DEFAULT: str(self.default),
            constants.PARAMETERS_GROUPS_CREATED: self.created_date,
            constants.PARAMETERS_GROUPS_MODIFIED: self.updated_date,
        }
