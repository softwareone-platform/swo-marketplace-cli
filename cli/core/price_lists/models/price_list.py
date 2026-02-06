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
    def from_dict(cls, source_dict: dict[str, Any]) -> Self:
        return cls(
            id=source_dict[constants.GENERAL_PRICELIST_ID]["value"],
            coordinate=source_dict[constants.GENERAL_PRICELIST_ID]["coordinate"],
            currency=source_dict[constants.GENERAL_CURRENCY]["value"],
            product_id=source_dict[constants.GENERAL_PRODUCT_ID]["value"],
            product_name=source_dict[constants.GENERAL_PRODUCT_NAME]["value"],
            vendor_id=source_dict[constants.GENERAL_VENDOR_ID]["value"],
            vendor_name=source_dict[constants.GENERAL_VENDOR_NAME]["value"],
            export_date=source_dict[constants.GENERAL_EXPORT_DATE]["value"].date(),
            precision=source_dict[constants.GENERAL_PRECISION]["value"],
            notes=source_dict[constants.GENERAL_NOTES]["value"],
            type=source_dict.get("type"),
            default_markup=source_dict.get(constants.GENERAL_DEFAULT_MARKUP, {}).get("value"),
            external_id=source_dict.get(constants.EXTERNAL_ID, {}).get("value"),
        )

    @classmethod
    @override
    def from_json(cls, json_dict: dict[str, Any]) -> Self:
        updated = json_dict["audit"].get("updated", {}).get("at")
        return cls(
            id=json_dict["id"],
            currency=json_dict["currency"],
            product_id=json_dict["product"]["id"],
            product_name=json_dict["product"]["name"],
            vendor_id=json_dict["vendor"]["id"],
            vendor_name=json_dict["vendor"]["name"],
            precision=json_dict["precision"],
            notes=json_dict.get("notes", ""),
            default_markup=json_dict["defaultMarkup"],
            external_id=json_dict.get("externalIds", {}).get("vendor"),
            created_date=parser.parse(json_dict["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        json_output = {
            "currency": self.currency,
            "precision": self.precision,
            "notes": self.notes,
            "product": self.product,
        }
        if self.is_operations():
            json_output["defaultMarkup"] = self.default_markup
        elif not self.is_operations() and self.external_id:
            json_output["externalIds"] = {"vendor": self.external_id}

        return json_output

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
