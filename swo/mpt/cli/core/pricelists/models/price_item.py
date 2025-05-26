from dataclasses import dataclass
from typing import Any

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.pricelists import constants


@dataclass
class PriceItemData(BaseDataModel):
    id: str
    coordinate: str
    status: str
    unit_lp: str
    unit_pp: str
    unit_sp: str | None
    markup: str | None
    type: str

    def is_operations(self) -> bool:
        return self.type == "operations"

    def is_vendor(self) -> bool:
        return self.type == "vendor"

    def is_draft(self) -> bool:
        return self.status == "Draft"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PriceItemData":
        return cls(
            id=data[constants.PRICELIST_ITEMS_ID]["value"],
            coordinate=data[constants.PRICELIST_ITEMS_ID]["coordinate"],
            status=data[constants.PRICELIST_ITEMS_STATUS]["value"],
            unit_lp=data[constants.PRICELIST_ITEMS_UNIT_LP]["value"],
            unit_pp=data[constants.PRICELIST_ITEMS_UNIT_PP]["value"],
            unit_sp=data.get(constants.PRICELIST_ITEMS_UNIT_SP, {}).get("value"),
            markup=data.get(constants.PRICELIST_ITEMS_MARKUP, {}).get("value"),
            type=data["type"],
        )

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "unitLP": self.unit_lp,
            "unitPP": self.unit_pp,
        }
        if self.is_vendor():
            data["status"] = self.status

        if self.is_operations():
            data["markup"] = self.markup
            if self.unit_sp is not None:
                data["unitSP"] = self.unit_sp

            if self.status != "Draft":
                data["status"] = self.status

        return data
