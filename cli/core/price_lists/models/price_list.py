import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Self, override

from cli.core.models import BaseDataModel
from cli.core.price_lists import constants
from dateutil import parser


@dataclass
class PriceListData(BaseDataModel):
    """Data model representing a price list."""

    id: str | None
    currency: str
    product_id: str
    product_name: str
    vendor_id: str
    vendor_name: str
    precision: int
    notes: str

    coordinate: str | None = None
    default_markup: float | None = None
    external_id: str | None = None
    export_date: dt.date = field(default_factory=dt.date.today)
    created_date: dt.date | None = None
    updated_date: dt.date | None = None
    # TODO: review this attr. Type depends on the account type, should we split into
    # operation and vendor model?
    type: str | None = None

    @property
    def product(self) -> dict[str, Any]:
        return {"id": self.product_id}

    def is_operations(self) -> bool:
        """Check if the price list type is 'operations'."""
        return self.type == "operations"

    @classmethod
    @override
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        return cls(
            id=row_data[constants.GENERAL_PRICELIST_ID]["value"],
            coordinate=row_data[constants.GENERAL_PRICELIST_ID]["coordinate"],
            currency=row_data[constants.GENERAL_CURRENCY]["value"],
            product_id=row_data[constants.GENERAL_PRODUCT_ID]["value"],
            product_name=row_data[constants.GENERAL_PRODUCT_NAME]["value"],
            vendor_id=row_data[constants.GENERAL_VENDOR_ID]["value"],
            vendor_name=row_data[constants.GENERAL_VENDOR_NAME]["value"],
            export_date=row_data[constants.GENERAL_EXPORT_DATE]["value"].date(),
            precision=row_data[constants.GENERAL_PRECISION]["value"],
            notes=row_data[constants.GENERAL_NOTES]["value"],
            type=row_data.get("type"),
            default_markup=row_data.get(constants.GENERAL_DEFAULT_MARKUP, {}).get("value"),
            external_id=row_data.get(constants.EXTERNAL_ID, {}).get("value"),
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        updated = json_data["audit"].get("updated", {}).get("at")
        return cls(
            id=json_data["id"],
            currency=json_data["currency"],
            product_id=json_data["product"]["id"],
            product_name=json_data["product"]["name"],
            vendor_id=json_data["vendor"]["id"],
            vendor_name=json_data["vendor"]["name"],
            precision=json_data["precision"],
            notes=json_data.get("notes", ""),
            default_markup=json_data["defaultMarkup"],
            external_id=json_data.get("externalIds", {}).get("vendor"),
            created_date=parser.parse(json_data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        json_payload = {
            "currency": self.currency,
            "precision": self.precision,
            "notes": self.notes,
            "product": self.product,
        }
        if self.is_operations():
            json_payload["defaultMarkup"] = self.default_markup
        elif not self.is_operations() and self.external_id:
            json_payload["externalIds"] = {"vendor": self.external_id}

        return json_payload

    @override
    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.GENERAL_PRICELIST_ID: self.id,
            constants.GENERAL_CURRENCY: self.currency,
            constants.GENERAL_PRODUCT_ID: self.product_id,
            constants.GENERAL_PRODUCT_NAME: self.product_name,
            constants.GENERAL_VENDOR_ID: self.vendor_id,
            constants.GENERAL_VENDOR_NAME: self.vendor_name,
            constants.GENERAL_EXPORT_DATE: self.export_date,
            constants.GENERAL_PRECISION: self.precision,
            constants.GENERAL_DEFAULT_MARKUP: self.default_markup,
            constants.GENERAL_NOTES: self.notes,
            constants.GENERAL_CREATED: self.created_date,
            constants.GENERAL_MODIFIED: self.updated_date,
            constants.EXTERNAL_ID: self.external_id,
        }
