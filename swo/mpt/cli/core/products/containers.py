from functools import partial

from dependency_injector import containers, providers
from swo.mpt.cli.core.accounts.containers import AccountContainer
from swo.mpt.cli.core.products.api import (
    ItemAPIService,
    ItemGroupAPIService,
    ParameterGroupAPIService,
    ParametersAPIService,
    ProductAPIService,
    TemplateAPIService,
)
from swo.mpt.cli.core.products.handlers import (
    AgreementParametersExcelFileManager,
    ItemExcelFileManager,
    ItemGroupExcelFileManager,
    ItemParametersExcelFileManager,
    ParameterGroupExcelFileManager,
    ProductExcelFileManager,
    RequestParametersExcelFileManager,
    SettingsExcelFileManager,
    SubscriptionParametersExcelFileManager,
    TemplateExcelFileManager,
)
from swo.mpt.cli.core.products.models import (
    AgreementParametersData,
    ItemData,
    ItemGroupData,
    ParameterGroupData,
    ProductData,
    TemplateData,
)
from swo.mpt.cli.core.products.services import (
    ItemGroupService,
    ItemService,
    ParameterGroupService,
    ParametersService,
    ProductService,
    TemplateService,
)
from swo.mpt.cli.core.services.service_context import ServiceContext


class ProductContainer(containers.DeclarativeContainer):
    """Container for product-related services and components.

    Attributes:
        config: Configuration provider for the container.
        account: Provides the active account.
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

    _account_container = providers.Container(AccountContainer)
    _mpt_client = providers.Singleton(_account_container.mpt_client)

    config = providers.Configuration()
    account = providers.Singleton(_account_container.account)

    _apis = providers.Dict(
        product=providers.Singleton(ProductAPIService, _mpt_client),
        items=providers.Singleton(ItemAPIService, _mpt_client, config.resource_id),
        item_group=providers.Singleton(ItemGroupAPIService, _mpt_client, config.resource_id),
        parameter_group=providers.Singleton(
            ParameterGroupAPIService, _mpt_client, config.resource_id
        ),
        parameters=providers.Singleton(ParametersAPIService, _mpt_client, config.resource_id),
        template=providers.Singleton(TemplateAPIService, _mpt_client, config.resource_id),
    )

    _file_managers = providers.Dict(
        product=providers.Singleton(ProductExcelFileManager, config.file_path),
        items=providers.Singleton(ItemExcelFileManager, config.file_path),
        item_group=providers.Singleton(ItemGroupExcelFileManager, config.file_path),
        parameter_group=providers.Singleton(ParameterGroupExcelFileManager, config.file_path),
        agreement_parameters=providers.Singleton(
            AgreementParametersExcelFileManager, config.file_path
        ),
        item_parameters=providers.Singleton(ItemParametersExcelFileManager, config.file_path),
        request_parameters=providers.Singleton(RequestParametersExcelFileManager, config.file_path),
        subscription_parameters=providers.Singleton(
            SubscriptionParametersExcelFileManager, config.file_path
        ),
        template=providers.Singleton(TemplateExcelFileManager, config.file_path),
        settings=providers.Singleton(SettingsExcelFileManager, config.file_path),
    )

    _services = {
        "product": {
            "api": _apis.provided["product"],
            "data_model": ProductData,
            "file_manager": _file_managers.provided["product"],
        },
        "items": {
            "api": _apis.provided["items"],
            "data_model": ItemData,
            "file_manager": _file_managers.provided["items"],
        },
        "item_group": {
            "api": _apis.provided["item_group"],
            "data_model": ItemGroupData,
            "file_manager": _file_managers.provided["item_group"],
        },
        "parameter_group": {
            "api": _apis.provided["parameter_group"],
            "data_model": ParameterGroupData,
            "file_manager": _file_managers.provided["parameter_group"],
        },
        "agreement_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": AgreementParametersData,
            "file_manager": _file_managers.provided["agreement_parameters"],
        },
        "item_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": AgreementParametersData,
            "file_manager": _file_managers.provided["item_parameters"],
        },
        "request_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": AgreementParametersData,
            "file_manager": _file_managers.provided["request_parameters"],
        },
        "subscription_parameters": {
            "api": _apis.provided["parameters"],
            "data_model": AgreementParametersData,
            "file_manager": _file_managers.provided["subscription_parameters"],
        },
        "template": {
            "api": _apis.provided["template"],
            "data_model": TemplateData,
            "file_manager": _file_managers.provided["template"],
        },
    }
    _partial_context = partial(
        providers.Factory, ServiceContext, account=account, stats=config.stats
    )

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
