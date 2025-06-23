from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)


class TemplateService(RelatedComponentsBaseService):
    def set_new_parameter_group(self, param_groups: DataCollectionModel) -> None:
        for data_model in self.file_manager.read_data():
            content = data_model.content

            for id, item in param_groups.collection.items():
                if id not in content:
                    continue

                content = content.replace(id, item.id)
                self.file_manager.write_id(data_model.content_coordinate, content)
