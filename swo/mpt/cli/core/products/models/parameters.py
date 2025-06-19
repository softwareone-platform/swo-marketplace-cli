import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants


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
    group_id: str
    name: str
    phase: str
    scope: str
    type: ScopeEnum
    constraints: dict[str, Any]
    options: dict[str, Any]
    created_group_id: str | None
    created_group_coordinate: str

    @property
    def group(self) -> dict[str, Any] | None:
        if self.is_order_request():
            return {"id": self.created_group_id}

        return None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        group_id = data[constants.PARAMETERS_GROUP_ID]["value"]
        created_group = data["parameter_groups_mapping"].get(group_id) if group_id else None
        return cls(
            id=data[constants.PARAMETERS_ID]["value"],
            coordinate=data[constants.PARAMETERS_ID]["coordinate"],
            description=data[constants.PARAMETERS_DESCRIPTION]["value"],
            display_order=data[constants.PARAMETERS_DISPLAY_ORDER]["value"],
            external_id=data[constants.PARAMETERS_EXTERNALID]["value"],
            name=data[constants.PARAMETERS_NAME]["value"],
            phase=data[constants.PARAMETERS_PHASE]["value"],
            scope=ScopeEnum(data["scope"]),
            type=data[constants.PARAMETERS_TYPE]["value"],
            constraints=json.loads(data[constants.PARAMETERS_CONSTRAINTS]["value"]),
            options=json.loads(data[constants.PARAMETERS_OPTIONS]["value"]),
            group_id=group_id,
            created_group_id=created_group.id if created_group else None,
            created_group_coordinate=data[constants.PARAMETERS_GROUP_ID]["coordinate"],
        )

    def is_order_request(self) -> bool:
        return self.phase == "Order" and self.scope not in ("Item", "Request")

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "scope": str(self.scope),
            "phase": self.phase,
            "type": self.type,
            "options": {key: value for key, value in self.options.items() if key != "label"},
            "constraints": self.constraints,
            "externalId": self.external_id,
            "displayOrder": self.display_order,
        }
        if self.is_order_request():
            data["group"] = self.group

        return data
