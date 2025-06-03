from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any, Self

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.price_lists import constants


class ItemAction(StrEnum):
    SKIP = "-"
    SKIPPED = ""
    UPDATE = "update"

    @classmethod
    def _missing_(cls, value):
        if value is None:
            return cls.SKIP

        return super()._missing_(value)


class ItemStatus(StrEnum):
    DRAFT = "Draft"
    FOR_SALE = "ForSale"
    PRIVATE = "Private"


@dataclass
class ItemData(BaseDataModel):
    id: str
    billing_frequency: str
    commitment: str
    erp_id: str | None
    item_id: str
    item_name: str
    markup: float | None
    status: ItemStatus
    unit_lp: float
    unit_pp: float
    unit_sp: float | None
    vendor_id: str

    action: ItemAction = ItemAction.SKIP
    coordinate: str | None = None
    modified_date: date | None = None
    type: str | None = None

    def is_operations(self) -> bool:
        return self.type == "operations"

    def is_vendor(self) -> bool:
        return self.type == "vendor"

    def to_update(self) -> bool:
        return self.action == ItemAction.UPDATE

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data[constants.PRICELIST_ITEMS_ID]["value"],
            coordinate=data[constants.PRICELIST_ITEMS_ID]["coordinate"],
            billing_frequency=data[constants.PRICELIST_ITEMS_BILLING_FREQUENCY]["value"],
            commitment=data[constants.PRICELIST_ITEMS_COMMITMENT]["value"],
            erp_id=data[constants.PRICELIST_ITEMS_ITEM_ERP_ID]["value"],
            item_id=data[constants.PRICELIST_ITEMS_ITEM_ID]["value"],
            item_name=data[constants.PRICELIST_ITEMS_ITEM_NAME]["value"],
            markup=data.get(constants.PRICELIST_ITEMS_MARKUP, {}).get("value"),
            status=ItemStatus(data[constants.PRICELIST_ITEMS_STATUS]["value"]),
            unit_lp=data[constants.PRICELIST_ITEMS_UNIT_LP]["value"],
            unit_pp=data[constants.PRICELIST_ITEMS_UNIT_PP]["value"],
            unit_sp=data.get(constants.PRICELIST_ITEMS_UNIT_SP, {}).get("value"),
            vendor_id=data[constants.PRICELIST_ITEMS_ITEM_VENDOR_ID]["value"],
            modified_date=data[constants.PRICELIST_ITEMS_MODIFIED]["value"].date(),
            action=ItemAction(data[constants.PRICELIST_ITEMS_ACTION]["value"]),
            type=data.get("type"),
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data.get("id", ""),
            billing_frequency=data["item"]["terms"]["period"],
            commitment=data["item"]["terms"]["commitment"],
            erp_id=data["item"]["externalIds"].get("operations"),
            item_id=data["item"]["id"],
            item_name=data["item"]["name"],
            markup=data["markup"],
            status=ItemStatus(data["status"]),
            unit_lp=data["unitLP"],
            unit_pp=data["unitPP"],
            unit_sp=data["unitSP"],
            vendor_id=data["item"]["externalIds"]["vendor"],
            action=ItemAction(data.get("action", ItemAction.SKIP)),
        )

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "unitLP": self.unit_lp,
            "unitPP": self.unit_pp,
        }
        if self.is_vendor():
            data["status"] = self.status.value

        if self.is_operations():
            data["markup"] = self.markup
            if self.unit_sp is not None:
                data["unitSP"] = self.unit_sp

            if self.status != "Draft":
                data["status"] = self.status.value

        return data
