from typing import Any, cast

from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.models.data_model import DataModel
from swo.mpt.cli.core.mpt.flows import search_uom_by_name
from swo.mpt.cli.core.products.constants import TAB_ITEMS
from swo.mpt.cli.core.products.models import ItemData
from swo.mpt.cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)
from swo.mpt.cli.core.services.service_result import ServiceResult


class ItemService(RelatedComponentsBaseService):
    # TODO: move to RelatedComponentsBaseService
    def update(self) -> ServiceResult:
        """
        Updates an existing item

        Returns:
            ServiceResult: The result of the update operation
        """
        errors = []
        for item in self.file_manager.read_data():
            item.product_id = self.resource_id
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
                    item.unit_id = search_uom_by_name(self.api.client, item.unit_name).id
                    item.type = "operations" if self.account.is_operations() else "vendor"
                    try:
                        new_item = self.api.post(json=item.to_json())
                    except MPTAPIError as e:
                        errors.append(str(e))
                        self._set_error(str(e), item.id)
                        continue

                    item.id = new_item["id"]
                else:
                    self.api.post_action(item.id, item.action)
            except Exception as e:
                errors.append(str(e))
                self._set_error(str(e), item.id)
                continue

            self._set_synced(item.id, item.coordinate)

        return ServiceResult(success=len(errors) == 0, errors=errors, model=None, stats=self.stats)

    def set_new_item_groups(self, item_groups: DataCollectionModel) -> None:
        for item in self.file_manager.read_data():
            try:
                new_group = item_groups.retrieve_by_id(item.group_id)
            except KeyError:
                continue

            self.file_manager.write_id(item.group_coordinate, new_group.id)

    def set_export_params(self) -> dict[str, Any]:
        params = super().set_export_params()
        params.update({"product.id": self.resource_id})
        return params

    def prepare_data_model_to_create(self, data_model: DataModel) -> DataModel:
        data_model = super().prepare_data_model_to_create(data_model)

        item = cast(ItemData, data_model)
        item.unit_id = search_uom_by_name(self.api.client, item.unit_name).id
        self.file_manager.write_id(item.unit_coordinate, item.unit_id)

        item.item_type = "operations" if self.account.is_operations() else "vendor"
        item.product_id = self.resource_id

        return data_model
