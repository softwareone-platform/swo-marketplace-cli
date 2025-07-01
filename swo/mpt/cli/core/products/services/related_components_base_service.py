from abc import ABC

from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.services import RelatedBaseService
from swo.mpt.cli.core.services.service_result import ServiceResult


class RelatedComponentsBaseService(RelatedBaseService, ABC):
    def create(self) -> ServiceResult:
        errors = []
        collection = {}
        for data_model in self.file_manager.read_data():
            try:
                new_item = self.api.post(json=data_model.to_json())
            except MPTAPIError as e:
                errors.append(str(e))
                self._set_error(str(e), data_model.id)
                continue

            old_id = data_model.id
            data_model.id = new_item["id"]
            collection[old_id] = data_model
            self._set_synced(new_item["id"], data_model.coordinate)

        return ServiceResult(
            success=len(errors) == 0,
            errors=errors,
            model=None,
            collection=DataCollectionModel(collection=collection),
            stats=self.stats,
        )

    def export(self) -> ServiceResult:  # pragma: no cover
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

    def update(self, product_id: str) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Updated method not implemented"], model=None, stats=self.stats
        )
