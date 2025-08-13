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
            except MPTAPIError as e:
                self.stats.add_error(TAB_PRICE_ITEMS)
                return ServiceResult(success=False, model=None, errors=[str(e)], stats=self.stats)

            data = [self.data_model.from_json(item) for item in response["data"]]
            self.file_manager.add(data)

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
        except MPTAPIError as e:
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        item_model = self.data_model.from_json(response.json())
        return ServiceResult(success=True, model=item_model, stats=self.stats)

    @override
    def update(self) -> ServiceResult:
        errors = []
        for item in self.file_manager.read_data():
            if not item.to_update():
                self._set_skipped()
                continue

            try:
                params = {"item.ExternalIds.vendor": item.vendor_id, "limit": 1}
                item_data = self.api.list(params=params)["data"][0]
            except MPTAPIError as e:
                errors.append(str(e))
                self._set_error(str(e), item.id)
                continue

            # TODO: this logic should be moved to the price list data model creation
            item.type = "operations" if self.account.is_operations() else "vendor"
            try:
                self.api.update(item_data["id"], item.to_json())
                self._set_synced(item.id, item.coordinate)
            except MPTAPIError as e:
                errors.append(f"Item {item.id}: {e!s}")
                self._set_error(str(e), item.id)
        return ServiceResult(success=len(errors) == 0, errors=errors, model=None, stats=self.stats)
