from dataclasses import dataclass, field
from datetime import date
from typing import Any, Self, override

from cli.core.models import BaseDataModel
from cli.core.price_lists import constants
from dateutil import parser


@dataclass
class PriceListData(BaseDataModel):
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
    export_date: date = field(default_factory=date.today)
    created_date: date | None = None
    updated_date: date | None = None
    # TODO: review this attr. Type depends on the account type, should we split into
    # operation and vendor model?
    type: str | None = None

    @property
    def product(self) -> dict[str, Any]:
        return {"id": self.product_id}

    def is_operations(self) -> bool:
        """Check if the price list type is 'operations'.

        Returns:
            True if the type is 'operations', False otherwise.

        """
        return self.type == "operations"

    @classmethod
    @override
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data[constants.GENERAL_PRICELIST_ID]["value"],
            coordinate=data[constants.GENERAL_PRICELIST_ID]["coordinate"],
            currency=data[constants.GENERAL_CURRENCY]["value"],
            product_id=data[constants.GENERAL_PRODUCT_ID]["value"],
            product_name=data[constants.GENERAL_PRODUCT_NAME]["value"],
            vendor_id=data[constants.GENERAL_VENDOR_ID]["value"],
            vendor_name=data[constants.GENERAL_VENDOR_NAME]["value"],
            export_date=data[constants.GENERAL_EXPORT_DATE]["value"].date(),
            precision=data[constants.GENERAL_PRECISION]["value"],
            notes=data[constants.GENERAL_NOTES]["value"],
            type=data.get("type"),
            default_markup=data.get(constants.GENERAL_DEFAULT_MARKUP, {}).get("value"),
            external_id=data.get(constants.EXTERNAL_ID, {}).get("value"),
        )

    @classmethod
    @override
    def from_json(cls, data: dict[str, Any]) -> Self:
        updated = data["audit"].get("updated", {}).get("at")
        return cls(
            id=data["id"],
            currency=data["currency"],
            product_id=data["product"]["id"],
            product_name=data["product"]["name"],
            vendor_id=data["vendor"]["id"],
            vendor_name=data["vendor"]["name"],
            precision=data["precision"],
            notes=data.get("notes", ""),
            default_markup=data["defaultMarkup"],
            external_id=data.get("externalIds", {}).get("vendor"),
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        data = {
            "currency": self.currency,
            "precision": self.precision,
            "notes": self.notes,
            "product": self.product,
        }
        if self.is_operations():
            data["defaultMarkup"] = self.default_markup
        elif not self.is_operations() and self.external_id:
            data["externalIds"] = {"vendor": self.external_id}

        return data

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
