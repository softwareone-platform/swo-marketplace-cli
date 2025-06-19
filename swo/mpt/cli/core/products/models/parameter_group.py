from dataclasses import dataclass
from datetime import date
from typing import Any, Self

from dateutil import parser
from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.products.models.data_actions import DataAction


@dataclass
class ParameterGroupData(BaseDataModel):
    id: str
    default: bool
    description: str
    display_order: int
    label: str
    name: str

    action: DataAction = DataAction.SKIP
    coordinate: str | None = None
    created_date: date | None = None
    updated_date: date | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        created_date = data[constants.PARAMETERS_GROUPS_CREATED].get("value")
        updated_date = data[constants.PARAMETERS_GROUPS_MODIFIED].get("value")
        return cls(
            id=data[constants.PARAMETERS_GROUPS_ID]["value"],
            coordinate=data[constants.PARAMETERS_GROUPS_ID]["coordinate"],
            default=data[constants.PARAMETERS_GROUPS_DEFAULT]["value"] == "True",
            description=data[constants.PARAMETERS_GROUPS_DESCRIPTION]["value"],
            display_order=data[constants.PARAMETERS_GROUPS_DISPLAY_ORDER]["value"],
            label=data[constants.PARAMETERS_GROUPS_LABEL]["value"],
            name=data[constants.PARAMETERS_GROUPS_NAME]["value"],
            created_date=created_date.date() if created_date else None,
            updated_date=updated_date.date() if updated_date else None,
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data["id"],
            description=data["description"],
            default=data["default"],
            display_order=data["displayOrder"],
            label=data["label"],
            name=data["name"],
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=parser.parse(data["audit"]["updated"]["at"]).date(),
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
            constants.PARAMETERS_GROUPS_DEFAULT: self.default,
            constants.PARAMETERS_GROUPS_CREATED: self.created_date,
            constants.PARAMETERS_GROUPS_MODIFIED: self.updated_date,
        }
