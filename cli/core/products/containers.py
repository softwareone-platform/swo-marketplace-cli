from functools import partial
from typing import Any, ClassVar

from cli.core.accounts.containers import AccountContainer
from cli.core.products import handlers as product_handlers
from cli.core.products import models as product_models
from cli.core.products.api import (
    ItemAPIService,
    ItemGroupAPIService,
    ParameterGroupAPIService,
    ParametersAPIService,
    ProductAPIService,
    TemplateAPIService,
)
from cli.core.products.handlers.parameters_excel_file_manager import AssetParametersExcelFileManager
from cli.core.products.services import (
    ItemGroupService,
    ItemService,
    ParameterGroupService,
    ParametersService,
    ProductService,
    TemplateService,
)
from cli.core.services.service_context import ServiceContext
from cli.core.stats import ProductStatsCollector
from dependency_injector import containers, providers


class ProductContainer(containers.DeclarativeContainer):
    """Container for product service.

    Attributes:
        product_service: Factory provider for the ProductService.
        item_service: Factory provider for the ItemService.
        item_group_service: Factory provider for the ItemGroupService.
        parameter_group_service: Factory provider for the ParameterGroupService.
        agreement_parameters_service: Factory provider for the Agreement parameters.
        item_parameters_service: Factory provider for the Item parameters.
        request_parameters_service: Factory provider for the Request parameters.
        subscription_parameters_service: Factory provider for the Subscription parameters.
        template_service: Factory provider for the TemplateService.

    """

    account_container = providers.Container(AccountContainer)
    _account = providers.Factory(account_container.account)
    _api_mpt_client = providers.Factory(account_container.api_mpt_client)
    resource_id = providers.Dependency(instance_of=str, default="")
    file_path = providers.Dependency(instance_of=str)
    stats = providers.Dependency(instance_of=ProductStatsCollector, default=ProductStatsCollector())
    _apis = providers.Dict(
        product=providers.Factory(ProductAPIService, _api_mpt_client),
        items=providers.Factory(ItemAPIService, _api_mpt_client, resource_id),
        item_group=providers.Factory(ItemGroupAPIService, _api_mpt_client, resource_id),
        parameter_group=providers.Factory(ParameterGroupAPIService, _api_mpt_client, resource_id),
        parameters=providers.Factory(ParametersAPIService, _api_mpt_client, resource_id),
        template=providers.Factory(TemplateAPIService, _api_mpt_client, resource_id),
    )

    _file_managers = providers.Dict(
        product=providers.Factory(product_handlers.ProductExcelFileManager, file_path),
        items=providers.Factory(product_handlers.ItemExcelFileManager, file_path),
        item_group=providers.Factory(product_handlers.ItemGroupExcelFileManager, file_path),
        parameter_group=providers.Factory(
            product_handlers.ParameterGroupExcelFileManager, file_path
        ),
        agreement_parameters=providers.Factory(
            product_handlers.AgreementParametersExcelFileManager, file_path
        ),
        asset_parameters=providers.Factory(AssetParametersExcelFileManager, file_path),
        item_parameters=providers.Factory(
            product_handlers.ItemParametersExcelFileManager, file_path
        ),
        request_parameters=providers.Factory(
            product_handlers.RequestParametersExcelFileManager, file_path
        ),
        subscription_parameters=providers.Factory(
            product_handlers.SubscriptionParametersExcelFileManager, file_path
        ),
        template=providers.Factory(product_handlers.TemplateExcelFileManager, file_path),
        settings=providers.Factory(product_handlers.SettingsExcelFileManager, file_path),
    )

    _services: ClassVar[dict[str, Any]] = {
        "product": {
            "api": _apis.provided["product"],
            "data_model": product_models.ProductData,
            "file_manager": _file_managers.provided["product"],
        },
        "items": {
            "api": _apis.provided["items"],
            "data_model": product_models.ItemData,
            "file_manager": _file_managers.provided["items"],
        },
        "item_group": {
            "api": _apis.provided["item_group"],
            "data_model": product_models.ItemGroupData,
            "file_manager": _file_managers.provided["item_group"],
        },
        "parameter_group": {
            "api": _apis.provided["parameter_group"],
            "data_model": product_models.ParameterGroupData,
            "file_manager": _file_managers.provided["parameter_group"],
        },
        "agreement_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": product_models.AgreementParametersData,
            "file_manager": _file_managers.provided["agreement_parameters"],
        },
        "asset_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": product_models.AssetParametersData,
            "file_manager": _file_managers.provided["asset_parameters"],
        },
        "item_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": product_models.ItemParametersData,
            "file_manager": _file_managers.provided["item_parameters"],
        },
        "request_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": product_models.RequestParametersData,
            "file_manager": _file_managers.provided["request_parameters"],
        },
        "subscription_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": product_models.SubscriptionParametersData,
            "file_manager": _file_managers.provided["subscription_parameters"],
        },
        "template": {
            "api": _apis.provided["template"],
            "data_model": product_models.TemplateData,
            "file_manager": _file_managers.provided["template"],
        },
    }
    _partial_context = partial(providers.Factory, ServiceContext, account=_account, stats=stats)

    product_service = providers.Factory(
        ProductService, service_context=_partial_context(**_services["product"])
    )
    item_service = providers.Factory(
        ItemService, service_context=_partial_context(**_services["items"])
    )
    item_group_service = providers.Factory(
        ItemGroupService, service_context=_partial_context(**_services["item_group"])
    )
    parameter_group_service = providers.Factory(
        ParameterGroupService, service_context=_partial_context(**_services["parameter_group"])
    )
    agreement_parameters_service = providers.Factory(
        ParametersService, service_context=_partial_context(**_services["agreement_parameters"])
    )
    asset_parameters_service = providers.Factory(
        ParametersService, service_context=_partial_context(**_services["asset_parameters"])
    )
    item_parameters_service = providers.Factory(
        ParametersService, service_context=_partial_context(**_services["item_parameters"])
    )
    request_parameters_service = providers.Factory(
        ParametersService, service_context=_partial_context(**_services["request_parameters"])
    )
    subscription_parameters_service = providers.Factory(
        ParametersService, service_context=_partial_context(**_services["subscription_parameters"])
    )
    template_service = providers.Factory(
        TemplateService, service_context=_partial_context(**_services["template"])
    )
