from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.pricelists.constants import TAB_PRICE_ITEMS
from swo.mpt.cli.core.services.base_service import BaseService
from swo.mpt.cli.core.services.service_result import ServiceResult


class ItemService(BaseService):
    def create(self) -> ServiceResult:
        return ServiceResult(
            success=False, errors=["Operation not implemented"], model=None, stats=self.stats
        )

    def retrieve(self) -> ServiceResult:
        return ServiceResult(
            success=False, errors=["Operation not implemented"], model=None, stats=self.stats
        )

    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        try:
            response = self.api.get(resource_id)
        except MPTAPIError as e:
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        item_model = self.data_model.from_json(response.json())
        return ServiceResult(success=True, model=item_model, stats=self.stats)

    def update(self, resource_id: str) -> ServiceResult:
        errors = []
        for item in self.file_handler.read_items_data():
            if not item.to_update():
                self._set_skipped()
                continue

            try:
                params = {"item.ExternalIds.vendor": item.vendor_id, "limit": 1}
                item_data = self.api.list(params=params)[0]
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
                errors.append(f"Item {item.id}: {str(e)}")
                self._set_error(str(e), item.id)
        return ServiceResult(success=len(errors) == 0, errors=errors, model=None, stats=self.stats)

    def _set_error(self, error: str, resource_id: str) -> None:
        self.file_handler.write_error(error, resource_id)
        self.stats.add_error(TAB_PRICE_ITEMS)

    def _set_synced(self, resource_id: str, item_coordinate: str) -> None:
        self.file_handler.write_id(item_coordinate, resource_id)
        self.stats.add_synced(TAB_PRICE_ITEMS)

    def _set_skipped(self):
        self.stats.add_skipped(TAB_PRICE_ITEMS)
