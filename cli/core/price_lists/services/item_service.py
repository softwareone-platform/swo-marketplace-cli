from typing import override

from cli.core.errors import MPTAPIError
from cli.core.price_lists.constants import (
    TAB_PRICE_ITEMS,
)
from cli.core.services import RelatedBaseService
from cli.core.services.service_result import ServiceResult


class ItemService(RelatedBaseService):
    """Service for managing price list item operations."""

    @override
    def create(self) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Operation not implemented"], model=None, stats=self.stats
        )

    @override
    def export(self) -> ServiceResult:
        self.file_manager.create_tab()

        offset = 0
        limit = 100
        select = "audit,item.terms,priceList.precision,priceList.currency"
        while True:
            try:
                response = self.api.list({"select": select, "offset": offset, "limit": limit})
            except MPTAPIError as error:
                self.stats.add_error(TAB_PRICE_ITEMS)
                return ServiceResult(
                    success=False, model=None, errors=[str(error)], stats=self.stats
                )

            records = [self.data_model.from_json(record) for record in response["data"]]
            self.file_manager.add(records)

            meta_data = response["meta"]
            if meta_data["offset"] + meta_data["limit"] < meta_data["total"]:
                offset += limit
            else:
                break

        return ServiceResult(success=True, model=None, stats=self.stats)

    @override
    def retrieve(self) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Operation not implemented"], model=None, stats=self.stats
        )

    @override
    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        try:
            response = self.api.get(resource_id)
        except MPTAPIError as error:
            return ServiceResult(success=False, errors=[str(error)], model=None, stats=self.stats)

        item_model = self.data_model.from_json(response.json())
        return ServiceResult(success=True, model=item_model, stats=self.stats)

    @override
    def update(self) -> ServiceResult:
        errors: list[str] = []
        for record in self.file_manager.read_data():
            if not record.to_update():
                self._set_skipped()
                continue

            self._update_record(errors, record)

        return ServiceResult(success=len(errors) == 0, errors=errors, model=None, stats=self.stats)

    def _update_item(self, item_data: dict, record) -> None:
        record.type = "operations" if self.account.is_operations() else "vendor"
        self.api.update(item_data["id"], record.to_json())

    def _update_record(self, errors: list[str], record) -> None:
        try:
            response = self.api.list(
                query_params={"item.ExternalIds.vendor": record.vendor_id, "limit": 1}
            )
        except (MPTAPIError, KeyError, ValueError) as error:
            errors.append(str(error))
            self._set_error(error, record.id)
            return

        response_data = response.get("data", [])
        if not response_data:
            missing_item_error = ValueError(
                f"Item {record.id}: no matching item found for vendor {record.vendor_id}"
            )
            errors.append(str(missing_item_error))
            self._set_error(missing_item_error, record.id)
            return

        try:
            self._update_item(response_data[0], record)
        except MPTAPIError as error:
            errors.append(f"Item {record.id}: {error!s}")
            self._set_error(error, record.id)
            return

        self._set_synced(record.id, record.coordinate)
