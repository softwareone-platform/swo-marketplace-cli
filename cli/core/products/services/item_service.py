from collections.abc import Callable
from typing import Any, cast, override

from cli.core.models import DataCollectionModel
from cli.core.models.data_model import DataModel
from cli.core.mpt.flows import search_uom_by_name
from cli.core.products.models import DataActionEnum, ItemActionEnum, ItemData
from cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)


class ItemService(RelatedComponentsBaseService):
    """Service for managing item operations."""

    @override
    def prepare_data_model_to_create(self, data_model: DataModel) -> DataModel:
        data_model = super().prepare_data_model_to_create(data_model)

        item = cast(ItemData, data_model)
        item.unit_id = search_uom_by_name(self.api.client, item.unit_name).id
        self.file_manager.write_ids({item.unit_coordinate: item.unit_id})

        item.item_type = "operations" if self.account.is_operations() else "vendor"
        item.product_id = self.resource_id

        return data_model

    def set_new_item_groups(self, item_groups: DataCollectionModel | None) -> None:
        """Update item group references in item content.

        Args:
            item_groups: A collection of item groups to update.

        """
        if item_groups is None or not item_groups.collection:
            return

        new_ids = {}
        for item in self.file_manager.read_data():
            try:
                new_group = item_groups.retrieve_by_id(item.group_id)
            except KeyError:
                continue

            new_ids[item.group_coordinate] = new_group.id

        if new_ids:
            self.file_manager.write_ids(new_ids)

        return

    @override
    def set_export_params(self) -> dict[str, Any]:
        params = super().set_export_params()
        params.update({"product.id": self.resource_id})
        return params

    def _action_create_item(self, data_model: DataModel):
        item = cast(ItemData, data_model)

        item.unit_id = search_uom_by_name(self.api.client, item.unit_name).id
        item.item_type = "operations" if self.account.is_operations() else "vendor"

        super()._action_create_item(data_model)

    def _action_post_action_item(self, data_model: DataModel) -> None:
        """
        Perform an action on the given data model.

        Args:
            data_model: The data model to perform the action on.

        """
        item = cast(ItemData, data_model)
        self.api.post_action(item.id, item.action)

    def _action_update_item(self, data_model: DataModel) -> None:
        item = cast(ItemData, data_model)

        params = {
            "externalIds.vendor": item.vendor_id,
            "product.id": item.product_id,
            "limit": 1,
        }
        item_data = self.api.list(params=params)["data"][0]
        item.id = item_data["id"]

        super()._action_update_item(data_model)

    def _get_update_action_handler(self, model_action: DataActionEnum) -> Callable:
        if model_action in {ItemActionEnum.REVIEW, ItemActionEnum.PUBLISH}:
            return self._action_post_action_item

        return super()._get_update_action_handler(model_action)
