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
    commitment: str | None
    erp_id: str | None
    item_id: str
    item_name: str
    markup: float | None
    status: ItemStatus
    unit_lp: float | None
    unit_pp: float | None
    unit_sp: float | None
    vendor_id: str

    action: ItemAction = ItemAction.SKIP
    coordinate: str | None = None
    lp_x1: float | None = None
    lp_xm: float | None = None
    lp_xy: float | None = None
    modified_date: date | None = None
    pp_x1: float | None = None
    pp_xm: float | None = None
    pp_xy: float | None = None
    sp_x1: float | None = None
    sp_xm: float | None = None
    sp_xy: float | None = None
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
            commitment=data["item"]["terms"].get("commitment"),
            erp_id=data["item"]["externalIds"].get("operations"),
            item_id=data["item"]["id"],
            item_name=data["item"]["name"],
            lp_x1=data.get("LPx1"),
            lp_xm=data.get("LPxM"),
            lp_xy=data.get("LPxY"),
            markup=data.get("markup"),
            pp_x1=data.get("PPx1"),
            pp_xm=data.get("PPxM"),
            pp_xy=data.get("PPxY"),
            sp_x1=data.get("SPx1"),
            sp_xm=data.get("SPxM"),
            sp_xy=data.get("SPxY"),
            status=ItemStatus(data["status"]),
            unit_lp=data.get("unitLP"),
            unit_pp=data.get("unitPP"),
            unit_sp=data.get("unitSP"),
            vendor_id=data["item"]["externalIds"]["vendor"],
            action=ItemAction.SKIP,
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

    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.PRICELIST_ITEMS_ID: self.id,
            constants.PRICELIST_ITEMS_ITEM_ID: self.item_id,
            constants.PRICELIST_ITEMS_ITEM_NAME: self.item_name,
            constants.PRICELIST_ITEMS_ITEM_VENDOR_ID: self.vendor_id,
            constants.PRICELIST_ITEMS_ITEM_ERP_ID: self.erp_id,
            constants.PRICELIST_ITEMS_BILLING_FREQUENCY: self.billing_frequency,
            constants.PRICELIST_ITEMS_COMMITMENT: self.commitment,
            constants.PRICELIST_ITEMS_UNIT_LP: self.unit_lp,
            constants.PRICELIST_ITEMS_UNIT_PP: self.unit_pp,
            constants.PRICELIST_ITEMS_MARKUP: self.markup,
            constants.PRICELIST_ITEMS_PPx1: self.pp_x1,
            constants.PRICELIST_ITEMS_PPxM: self.pp_xm,
            constants.PRICELIST_ITEMS_PPxY: self.pp_xy,
            constants.PRICELIST_ITEMS_UNIT_SP: self.unit_sp,
            constants.PRICELIST_ITEMS_SPx1: self.sp_x1,
            constants.PRICELIST_ITEMS_SPxM: self.sp_xm,
            constants.PRICELIST_ITEMS_SPxY: self.sp_xy,
            constants.PRICELIST_ITEMS_LPx1: self.lp_x1,
            constants.PRICELIST_ITEMS_LPxM: self.lp_xm,
            constants.PRICELIST_ITEMS_LPxY: self.lp_xy,
            constants.PRICELIST_ITEMS_STATUS: self.status.value,
            constants.PRICELIST_ITEMS_ACTION: self.action.value,
            constants.PRICELIST_ITEMS_MODIFIED: self.modified_date,
        }
