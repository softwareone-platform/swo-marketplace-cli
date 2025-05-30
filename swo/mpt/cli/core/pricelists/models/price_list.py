from dataclasses import dataclass
from typing import Any

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.pricelists import constants


@dataclass
class PriceListData(BaseDataModel):
    id: str
    coordinate: str
    currency: str
    precision: int
    notes: str
    product_id: int
    type: str
    default_markup: str | None = None
    external_id: str | None = None

    @property
    def product(self) -> dict[str, Any]:
        return {"id": self.product_id}

    def is_operations(self) -> bool:
        return self.type == "operations"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PriceListData":
        return cls(
            id=data[constants.GENERAL_PRICELIST_ID]["value"],
            coordinate=data[constants.GENERAL_PRICELIST_ID]["coordinate"],
            currency=data[constants.GENERAL_CURRENCY]["value"],
            precision=data[constants.GENERAL_PRECISION]["value"],
            notes=data[constants.GENERAL_NOTES]["value"],
            product_id=data[constants.GENERAL_PRODUCT_ID]["value"],
            type=data["type"],
            default_markup=data.get(constants.GENERAL_DEFAULT_MARKUP, {}).get("value"),
            external_id=data.get(constants.EXTERNAL_ID, {}).get("value"),
        )

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
