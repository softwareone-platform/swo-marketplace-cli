import datetime as dt
from dataclasses import dataclass
from typing import Any, Self, override

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models.mixins import ActionMixin
from dateutil import parser


@dataclass
class ParameterGroupData(BaseDataModel, ActionMixin):
    """Data model representing a parameter group."""

    id: str
    default: bool
    display_order: int
    label: str
    name: str

    coordinate: str | None = None
    description: str | None = None
    created_date: dt.date | None = None
    updated_date: dt.date | None = None

    @classmethod
    @override
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        return cls(
            id=row_data[constants.PARAMETERS_GROUPS_ID]["value"],
            coordinate=row_data[constants.PARAMETERS_GROUPS_ID]["coordinate"],
            default=row_data[constants.PARAMETERS_GROUPS_DEFAULT]["value"] == "True",
            description=row_data[constants.PARAMETERS_GROUPS_DESCRIPTION]["value"],
            display_order=int(row_data[constants.PARAMETERS_GROUPS_DISPLAY_ORDER]["value"]),
            label=row_data[constants.PARAMETERS_GROUPS_LABEL]["value"],
            name=row_data[constants.PARAMETERS_GROUPS_NAME]["value"],
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        updated = json_data["audit"].get("updated", {}).get("at")
        return cls(
            id=json_data["id"],
            description=json_data.get("description"),
            default=json_data["default"],
            display_order=json_data["displayOrder"],
            label=json_data["label"],
            name=json_data["name"],
            created_date=parser.parse(json_data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        return {
            "default": self.default,
            "description": self.description,
            "displayOrder": self.display_order,
            "label": self.label,
            "name": self.name,
        }

    @override
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
