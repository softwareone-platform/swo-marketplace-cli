from dataclasses import dataclass, field
from datetime import date
from typing import Any, Self

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models.enums import ItemTermsModelEnum
from cli.core.products.models.mixins import ItemActionMixin
from dateutil import parser


@dataclass
class ItemData(BaseDataModel, ItemActionMixin):
    id: str
    description: str
    group_id: str
    name: str
    quantity_not_applicable: bool
    terms_model: ItemTermsModelEnum
    terms_period: str
    terms_commitment: str | None
    unit_id: str
    vendor_id: str

    coordinate: str | None = None
    group_coordinate: str | None = None
    group_name: str | None = None
    item_type: str | None = None
    operations_id: str | None = None
    parameters: list[dict[str, Any]] = field(default_factory=list)
    product_id: str | None = None
    status: str | None = None
    unit_coordinate: str | None = None
    unit_name: str | None = None
    created_date: date | None = None
    updated_date: date | None = None

    @property
    def external_ids(self):
        return self.operations_id if self.item_type == "operations" else self.vendor_id

    @property
    def group(self) -> dict[str, Any]:
        return {"id": self.group_id}

    @property
    def product(self) -> dict[str, Any]:
        return {"id": self.product_id}

    @property
    def terms(self) -> dict[str, Any]:
        data: dict[str, Any] = {"model": self.terms_model.value}

        if self.terms_model == ItemTermsModelEnum.ONE_TIME:
            data["period"] = self.terms_model.value
        else:
            data["commitment"] = self.terms_commitment
            data["period"] = self.terms_period

        return data

    @property
    def unit(self) -> dict[str, Any]:
        return {"id": self.unit_id}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        try:
            group_id = data["group_id"]
        except KeyError:
            group_id = data[constants.ITEMS_GROUP_ID]["value"]

        return cls(
            id=data[constants.ITEMS_ID]["value"],
            action=data[constants.ITEMS_ACTION]["value"],
            coordinate=data[constants.ITEMS_ID]["coordinate"],
            description=data[constants.ITEMS_DESCRIPTION]["value"],
            group_id=group_id,
            group_coordinate=data[constants.ITEMS_GROUP_ID]["coordinate"],
            item_type="operations" if data.get("is_operations", False) else "vendor",
            name=data[constants.ITEMS_NAME]["value"],
            terms_commitment=data[constants.ITEMS_TERMS_COMMITMENT]["value"],
            terms_model=ItemTermsModelEnum(data[constants.ITEMS_TERMS_MODEL]["value"]),
            terms_period=data[constants.ITEMS_TERMS_PERIOD]["value"],
            quantity_not_applicable=data[constants.ITEMS_QUANTITY_APPLICABLE]["value"] == "True",
            unit_name=data[constants.ITEMS_UNIT_NAME]["value"],
            unit_coordinate=data[constants.ITEMS_UNIT_ID]["coordinate"],
            vendor_id=data[constants.ITEMS_VENDOR_ITEM_ID]["value"],
            group_name=data.get(constants.ITEMS_GROUP_NAME, {}).get("value"),
            operations_id=data.get(constants.ITEMS_ERP_ITEM_ID, {}).get("value"),
            parameters=data.get("parameters", []),
            unit_id=data.get(constants.ITEMS_UNIT_ID, {}).get("value"),
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        updated = data["audit"].get("updated", {}).get("at")
        return cls(
            id=data["id"],
            description=data["description"],
            group_id=data["group"]["id"],
            group_name=data["group"]["name"],
            name=data["name"],
            product_id=data["product"]["id"],
            quantity_not_applicable=data["quantityNotApplicable"],
            terms_commitment=data["terms"].get("commitment"),
            terms_model=ItemTermsModelEnum(data["terms"]["model"]),
            terms_period=data["terms"]["period"],
            unit_id=data["unit"]["id"],
            vendor_id=data["externalIds"]["vendor"],
            operations_id=data["externalIds"].get("operations"),
            parameters=[],
            status=data["status"],
            unit_name=data["unit"]["name"],
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=updated and parser.parse(updated).date() or None,
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

    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.ITEMS_ID: self.id,
            constants.ITEMS_NAME: self.name,
            constants.ITEMS_ACTION: self.action,
            constants.ITEMS_VENDOR_ITEM_ID: self.vendor_id,
            constants.ITEMS_ERP_ITEM_ID: self.operations_id,
            constants.ITEMS_DESCRIPTION: self.description,
            constants.ITEMS_TERMS_MODEL: self.terms_model,
            constants.ITEMS_TERMS_PERIOD: self.terms_period,
            constants.ITEMS_TERMS_COMMITMENT: self.terms_commitment,
            constants.ITEMS_STATUS: self.status,
            constants.ITEMS_GROUP_ID: self.group_id,
            constants.ITEMS_GROUP_NAME: self.group_name,
            constants.ITEMS_UNIT_ID: self.unit_id,
            constants.ITEMS_UNIT_NAME: self.unit_name,
            constants.ITEMS_QUANTITY_APPLICABLE: str(self.quantity_not_applicable),
            constants.ITEMS_CREATED: self.created_date,
            constants.ITEMS_MODIFIED: self.updated_date,
        }
