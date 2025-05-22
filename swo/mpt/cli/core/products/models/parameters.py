import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants



@dataclass
class ParameterGroupData(BaseDataModel):
    id: str
    name: str
    coordinate: str | None = None
    label: str | None = None
    description: str | None = None
    displayOrder: str | None = None
    default: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParameterGroupData":
        return cls(
            id=data[constants.PARAMETERS_GROUPS_ID]["value"],
            coordinate=data[constants.PARAMETERS_GROUPS_ID]["coordinate"],
            name=data[constants.PARAMETERS_GROUPS_NAME]["value"],
            label=data[constants.PARAMETERS_GROUPS_LABEL]["value"],
            description=data[constants.PARAMETERS_GROUPS_DESCRIPTION]["value"],
            displayOrder=data[constants.PARAMETERS_GROUPS_DISPLAY_ORDER]["value"],
            default=data[constants.PARAMETERS_GROUPS_DEFAULT]["value"] == "True",
        )


    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "displayOrder": self.displayOrder,
            "default": self.default,
        }


class ScopeEnum(StrEnum):
    AGREEMENT = "Agreement"
    ITEM = "Item"
    REQUEST = "Request"
    SUBSCRIPTION = "Subscription"

@dataclass
class ParametersData(BaseDataModel):
    id: str
    coordinate: str
    description: str
    display_order: str
    external_id: str
    name: str
    phase: str
    scope: str
    type: ScopeEnum
    constraints: dict[str, Any]
    options: dict[str, Any]
    parameter_groups_mapping: dict[str, Any]
    parameter_groups: dict[str, ParameterGroupData] = None

    @property
    def group(self) -> dict[str, Any] | None:
        if self.is_order_request():
            return {
                "id": self.parameter_groups_mapping[self.id]
            }
        return  None

    @property
    def group_id(self) -> str | None:
        return self.group["id"] if self.group else None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParametersData":
        return cls(
            id=data[constants.ID_COLUMN_NAME]["value"],
            coordinate=data[constants.ID_COLUMN_NAME]["coordinate"],
            description=data[constants.PARAMETERS_DESCRIPTION]["value"],
            display_order=data[constants.PARAMETERS_DISPLAY_ORDER]["value"],
            external_id=data[constants.PARAMETERS_EXTERNALID]["value"],
            name=data[constants.PARAMETERS_NAME]["value"],
            phase=data[constants.PARAMETERS_PHASE]["value"],
            scope=ScopeEnum(data["scope"]),
            type=data[constants.PARAMETERS_TYPE]["value"],
            constraints=json.loads(data[constants.PARAMETERS_CONSTRAINTS]["value"]),
            options=json.loads(data[constants.PARAMETERS_OPTIONS]["value"]),
            parameter_groups_mapping=data["parameter_groups_mapping"]
        )

    def is_order_request(self) -> bool:
        return self.phase == "Order" and self.scope not in ("Item", "Request")

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
            "phase": self.phase,
            "type": self.type,
            "options": {key: value for key, value in self.options.items() if key != "label"},
            "constraints": self.constraints,
            "externalId": self.external_id,
            "displayOrder": self.display_order,
            "group": self.group,
        }
