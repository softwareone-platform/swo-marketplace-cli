from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)


class ParametersService(RelatedComponentsBaseService):
    def set_new_parameter_group(self, parameter_groups: DataCollectionModel) -> None:
        for data_model in self.file_manager.read_data():
            try:
                new_group = parameter_groups.retrieve_by_id(data_model.group_id)
            except KeyError:
                continue

            self.file_manager.write_id(data_model.group_id_coordinate, new_group.id)
