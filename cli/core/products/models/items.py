import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Self, override

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models.enums import ItemTermsModelEnum
from cli.core.products.models.mixins import ItemActionMixin
from dateutil import parser


@dataclass
class ItemData(BaseDataModel, ItemActionMixin):
    """Data model representing a product item."""

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
    parameter_values: list[dict[str, Any]] = field(default_factory=list)
    product_id: str | None = None
    status: str | None = None
    unit_coordinate: str | None = None
    unit_name: str | None = None
    created_date: dt.date | None = None
    updated_date: dt.date | None = None

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
        terms_payload: dict[str, Any] = {"model": self.terms_model.value}

        if self.terms_model == ItemTermsModelEnum.ONE_TIME:
            terms_payload["period"] = self.terms_model.value
        else:
            terms_payload["commitment"] = self.terms_commitment
            terms_payload["period"] = self.terms_period

        return terms_payload

    @property
    def unit(self) -> dict[str, Any]:
        return {"id": self.unit_id}

    @classmethod
    @override
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        try:
            group_id = row_data["group_id"]
        except KeyError:
            group_id = row_data[constants.ITEMS_GROUP_ID]["value"]

        return cls(
            id=row_data[constants.ITEMS_ID]["value"],
            action=row_data[constants.ITEMS_ACTION]["value"],
            coordinate=row_data[constants.ITEMS_ID]["coordinate"],
            description=row_data[constants.ITEMS_DESCRIPTION]["value"],
            group_id=group_id,
            group_coordinate=row_data[constants.ITEMS_GROUP_ID]["coordinate"],
            item_type="operations" if row_data.get("is_operations") else "vendor",
            name=row_data[constants.ITEMS_NAME]["value"],
            terms_commitment=row_data[constants.ITEMS_TERMS_COMMITMENT]["value"],
            terms_model=ItemTermsModelEnum(row_data[constants.ITEMS_TERMS_MODEL]["value"]),
            terms_period=row_data[constants.ITEMS_TERMS_PERIOD]["value"],
            quantity_not_applicable=row_data[constants.ITEMS_QUANTITY_APPLICABLE]["value"]
            == "True",
            unit_name=row_data[constants.ITEMS_UNIT_NAME]["value"],
            unit_coordinate=row_data[constants.ITEMS_UNIT_ID]["coordinate"],
            vendor_id=row_data[constants.ITEMS_VENDOR_ITEM_ID]["value"],
            group_name=row_data.get(constants.ITEMS_GROUP_NAME, {}).get("value"),
            operations_id=row_data.get(constants.ITEMS_ERP_ITEM_ID, {}).get("value"),
            parameter_values=row_data.get("parameters", []),
            unit_id=row_data.get(constants.ITEMS_UNIT_ID, {}).get("value"),
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        updated = json_data["audit"].get("updated", {}).get("at")
        return cls(
            id=json_data["id"],
            description=json_data["description"],
            group_id=json_data["group"]["id"],
            group_name=json_data["group"]["name"],
            name=json_data["name"],
            product_id=json_data["product"]["id"],
            quantity_not_applicable=json_data["quantityNotApplicable"],
            terms_commitment=json_data["terms"].get("commitment"),
            terms_model=ItemTermsModelEnum(json_data["terms"]["model"]),
            terms_period=json_data["terms"]["period"],
            unit_id=json_data["unit"]["id"],
            vendor_id=json_data["externalIds"]["vendor"],
            operations_id=json_data["externalIds"].get("operations"),
            parameter_values=[],
            status=json_data["status"],
            unit_name=json_data["unit"]["name"],
            created_date=parser.parse(json_data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    @override
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
            "parameters": self.parameter_values,
        }

    @override
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
