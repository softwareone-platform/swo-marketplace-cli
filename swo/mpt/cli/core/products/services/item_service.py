from typing import Any

from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.products.constants import TAB_ITEMS
from swo.mpt.cli.core.services.base_service import BaseService
from swo.mpt.cli.core.services.service_result import ServiceResult


class ItemService(BaseService):
    def create(self) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Create method not implemented"], model=None, stats=self.stats
        )

    def export(self, context: dict[str, Any]) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Export method not implemented"], model=None, stats=self.stats
        )

    def retrieve(self) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Retrieve not implemented"], model=None, stats=self.stats
        )

    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False,
            errors=["Retrieve from mpt not implemented"],
            model=None,
            stats=self.stats,
        )

    def update(self, product_id: str) -> ServiceResult:
        """
        Updates an existing item

        Args:
            product_id: The product ID related to the items to update

        Returns:
            ServiceResult: The result of the update operation
        """
        errors = []
        for item in self.file_manager.read_data():
            item.product_id = product_id
            if item.to_skip:
                self.stats.add_skipped(TAB_ITEMS)
                continue
            try:
                if item.to_update:
                    try:
                        params = {
                            "externalIds.vendor": item.vendor_id,
                            "product.id": item.product_id,
                            "limit": 1,
                        }
                        item_data = self.api.list(params=params)["data"][0]
                    except MPTAPIError as e:
                        errors.append(str(e))
                        self._set_error(str(e), item.id)
                        continue

                    item.id = item_data["id"]
                    self.api.update(item.id, item.to_json())

                elif item.to_create:
                    # TODO: move the get logic to the api service
                    from swo.mpt.cli.core.products.flows import set_unit_of_measure

                    set_unit_of_measure(self.api.client, item)
                    item.type = "operations" if self.account.is_operations() else "vendor"
                    new_item = self.api.post(item.to_json())
                    item.id = new_item["id"]
                else:
                    self.api.post_action(item.id, item.action)
            except Exception as e:
                errors.append(str(e))
                self._set_error(str(e), item.id)
                continue

            self._set_synced(item.id, item.coordinate)

        return ServiceResult(success=len(errors) == 0, errors=errors, model=None, stats=self.stats)
