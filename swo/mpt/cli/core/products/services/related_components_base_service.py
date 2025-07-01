from abc import ABC

from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.models.data_model import DataModel
from swo.mpt.cli.core.services import RelatedBaseService
from swo.mpt.cli.core.services.service_result import ServiceResult


class RelatedComponentsBaseService(RelatedBaseService, ABC):
    def create(self) -> ServiceResult:
        errors = []
        collection = {}
        for data_model in self.file_manager.read_data():
            data_model = self.prepare_data_model_to_create(data_model)

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

    def export(self) -> ServiceResult:
        self.file_manager.create_tab()
        params = self.export_params
        while True:
            try:
                response = self.api.list(params=params)
            except MPTAPIError as e:
                self._set_error(str(e))
                return ServiceResult(success=False, model=None, errors=[str(e)], stats=self.stats)

            self.file_manager.add([self.data_model.from_json(item) for item in response["data"]])

            meta_data = response["meta"]
            if meta_data["offset"] + meta_data["limit"] < meta_data["total"]:
                params["offset"] += params["limit"]
            else:
                break

        return ServiceResult(success=True, model=None, stats=self.stats)

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

    def update(self) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Updated method not implemented"], model=None, stats=self.stats
        )

    def prepare_data_model_to_create(self, data_model: DataModel) -> DataModel:
        """
        Hook method to customize the data model before creating it. Subclasses can override this
        method to modify data or add the logic needed before sending to API.

        Args:
            data_model: The data model to be customized

        Returns:
             DataModel: The data model to create
        """
        return data_model
