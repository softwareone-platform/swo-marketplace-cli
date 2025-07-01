from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.mpt.flows import search_uom_by_name
from swo.mpt.cli.core.products.constants import TAB_ITEMS
from swo.mpt.cli.core.products.models import ItemData
from swo.mpt.cli.core.services import BaseService
from swo.mpt.cli.core.services.service_result import ServiceResult


class ItemService(BaseService):
    def create(self, **kwargs) -> ServiceResult:
        errors = []
        for item in self.file_manager.read_data():
            item.unit_id = self._get_unit_of_measure_id(item)
            item.type = "operations" if self.account.is_operations() else "vendor"
            item.product_id = kwargs["product_id"]
            try:
                new_item = self.api.post(json=item.to_json())
            except MPTAPIError as e:
                errors.append(str(e))
                self._set_error(str(e), item.id)
                continue

            item.id = new_item["id"]
            self._set_synced(item.id, item.coordinate)

            self.file_manager.write_id(item.unit_coordinate, item.unit_id)

        return ServiceResult(success=len(errors) == 0, errors=errors, model=None, stats=self.stats)

    def export(self, resource_id: str) -> ServiceResult:  # pragma: no cover
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
                    item.unit_id = self._get_unit_of_measure_id(item)
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

    def _get_unit_of_measure_id(self, item: ItemData) -> str:
        return search_uom_by_name(self.api.client, item.unit_name).id
