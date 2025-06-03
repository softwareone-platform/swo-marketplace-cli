from dataclasses import dataclass, field
from typing import Any, Self

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants


@dataclass
class ItemData(BaseDataModel):
    id: str
    coordinate: str
    name: str
    description: str
    group_id: str
    group_coordinate: str
    product_id: str
    quantity_not_applicable: bool
    unit_id: str
    unit_coordinate: str
    period: str
    item_type: str
    external_ids: str
    commitment: str
    parameters: list[dict[str, Any]] = field(default_factory=list)

    @property
    def group(self) -> dict[str, Any]:
        return {"id": self.group_id}

    @property
    def product(self) -> dict[str, Any]:
        return {"id": self.product_id}

    @property
    def terms(self) -> dict[str, Any]:
        data = {"period": self.period}
        if self.period != "one-time":
            data["commitment"] = self.commitment

        return data

    @property
    def unit(self) -> dict[str, Any]:
        return {"id": self.unit_id}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        if data.get("is_operations", False):
            item_type = "operations"
            external_ids = data[constants.ITEMS_ERP_ITEM_ID]["value"]
        else:
            item_type = "vendor"
            external_ids = data[constants.ITEMS_VENDOR_ITEM_ID]["value"]

        try:
            group_id = data["group_id"]
        except KeyError:
            group_id = data[constants.ITEMS_GROUP_ID]["value"]

        return cls(
            id=data[constants.ITEMS_ID]["value"],
            coordinate=data[constants.ITEMS_ID]["coordinate"],
            name=data[constants.ITEMS_NAME]["value"],
            description=data[constants.ITEMS_DESCRIPTION]["value"],
            group_id=group_id,
            group_coordinate=data[constants.ITEMS_GROUP_ID]["coordinate"],
            product_id=data["product_id"],
            quantity_not_applicable=data[constants.ITEMS_QUANTITY_APPLICABLE]["value"] == "True",
            unit_id=data[constants.ITEMS_UNIT_ID]["value"],
            unit_coordinate=data[constants.ITEMS_UNIT_ID]["coordinate"],
            parameters=data.get("parameters", []),
            period=data[constants.ITEMS_BILLING_FREQUENCY]["value"],
            commitment=data.get(constants.ITEMS_COMMITMENT_TERM, {}).get("value"),
            item_type=item_type,
            external_ids=external_ids,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "externalIds": {self.item_type: self.external_ids},
            "group": self.group,
            "product": self.product,
            "quantityNotApplicable": self.quantity_not_applicable,
            "terms": self.terms,
            "unit": self.unit,
            "parameters": self.parameters,
        }


@dataclass
class ItemGroupData(BaseDataModel):
    id: str
    coordinate: str
    name: str
    label: str
    description: str
    display_order: str
    default: bool
    multiple: bool
    required: bool

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
