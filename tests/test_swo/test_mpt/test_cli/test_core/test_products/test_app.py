from unittest.mock import Mock
from urllib.parse import urljoin

from swo.mpt.cli.core.models import DataCollectionModel
from swo.mpt.cli.core.products import app
from swo.mpt.cli.core.products.app import create_product, update_product
from swo.mpt.cli.core.products.services import (
    ItemGroupService,
    ItemService,
    ParameterGroupService,
    ParametersService,
    ProductService,
    TemplateService,
)
from swo.mpt.cli.core.services.service_result import ServiceResult
from swo.mpt.cli.core.stats import ProductStatsCollector
from typer.testing import CliRunner

runner = CliRunner()


def test_list_products(
    expected_account, mocker, requests_mocker, mpt_client, mpt_products_response
):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            "/catalog/products?limit=10&offset=0",
            allow_fragments=True,
        ),
        json=mpt_products_response,
    )

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0, result.stdout
    assert mpt_products_response["data"][0]["id"] in result.stdout


def test_list_products_with_query_and_paging(
    expected_account, mocker, requests_mocker, mpt_client, mpt_products_response
):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    requests_mocker.get(
        urljoin(
            mpt_client.base_url,
            "/catalog/products?limit=20&offset=0&eq(product.id,PRD-1234)",
            allow_fragments=True,
        ),
        json=mpt_products_response,
    )

    result = runner.invoke(
        app,
        ["list", "--page", "20", "--query", "eq(product.id,PRD-1234)"],
    )

    assert result.exit_code == 0, result.stdout
    assert mpt_products_response["data"][0]["id"] in result.stdout


def test_file_with_extension(expected_account, mocker):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)


def test_sync_file_doesnt_exist(expected_account, mocker):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)

    result = runner.invoke(
        app,
        ["sync", "--dry-run", "some-file"],
    )

    assert result.exit_code == 3, result.stdout
    assert "Provided file path doesn't exist" in result.stdout


def test_sync_with_dry_run_failure(expected_account, mocker, product_empty_file):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)

    result = runner.invoke(
        app,
        ["sync", "--dry-run", str(product_empty_file)],
    )

    assert result.exit_code == 3, result.stdout
    assert "General: Required tab doesn't exist" in result.stdout


def test_sync_with_dry_run(expected_account, mocker, product_new_file):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    create_mock = mocker.patch("swo.mpt.cli.core.products.app.create_product")
    update_mock = mocker.patch("swo.mpt.cli.core.products.app.update_product")

    result = runner.invoke(
        app,
        ["sync", "--dry-run", str(product_new_file)],
    )

    assert result.exit_code == 0, result.stdout
    assert "Product definition" in result.stdout
    create_mock.assert_not_called()
    update_mock.assert_not_called()


def test_sync_product_update(
    mocker, expected_account, product_new_file, product, product_data_from_dict
):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    stats_mock = Mock(spec=ProductStatsCollector, is_error=False, to_table=Mock(return_value=""))
    validate_definition_mock = mocker.patch.object(
        ProductService,
        "validate_definition",
        return_value=ServiceResult(success=True, model=None, stats=stats_mock),
    )
    retrieve_mock = mocker.patch.object(
        ProductService,
        "retrieve",
        return_value=ServiceResult(success=True, model=product_data_from_dict, stats=stats_mock),
    )
    update_product = mocker.patch(
        "swo.mpt.cli.core.products.app.update_product", return_value=(stats_mock, product)
    )

    result = runner.invoke(
        app,
        ["sync", str(product_new_file)],
        input="y\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Do you want to update product" in result.stdout
    validate_definition_mock.assert_called_once()
    retrieve_mock.assert_called_once()
    update_product.assert_called_once()


def test_sync_product_update_error(
    mocker, expected_account, product_new_file, product, product_data_from_dict
):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    stats_mock = Mock(spec=ProductStatsCollector, is_error=True, to_table=Mock(return_value=""))
    validate_definition_mock = mocker.patch.object(
        ProductService,
        "validate_definition",
        return_value=ServiceResult(success=True, model=None, stats=stats_mock),
    )
    retrieve_mock = mocker.patch.object(
        ProductService,
        "retrieve",
        return_value=ServiceResult(success=True, model=product_data_from_dict, stats=stats_mock),
    )
    update_product = mocker.patch(
        "swo.mpt.cli.core.products.app.update_product", return_value=(stats_mock, product)
    )

    result = runner.invoke(
        app,
        ["sync", str(product_new_file)],
        input="y\n",
    )

    assert result.exit_code == 3, result.stdout
    validate_definition_mock.assert_called_once()
    retrieve_mock.assert_called_once()
    update_product.assert_called_once()


def test_sync_product_force_create(
    mocker, expected_account, product_new_file, product_data_from_dict
):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    stats_mock = Mock(spec=ProductStatsCollector, is_error=False, to_table=Mock(return_value=""))
    validate_definition_mock = mocker.patch.object(
        ProductService,
        "validate_definition",
        return_value=ServiceResult(success=True, model=None, stats=stats_mock),
    )
    retrieve_mock = mocker.patch.object(
        ProductService,
        "retrieve",
        return_value=ServiceResult(success=True, model=product_data_from_dict, stats=stats_mock),
    )
    create_product_mock = mocker.patch(
        "swo.mpt.cli.core.products.app.create_product",
        return_value=(stats_mock, product_data_from_dict),
    )

    result = runner.invoke(
        app,
        ["sync", "--force-create", str(product_new_file)],
        input="y\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Do you want to create new" in result.stdout
    validate_definition_mock.assert_called_once()
    retrieve_mock.assert_called_once()
    create_product_mock.assert_called_once()
    stats_mock.to_table.assert_called_once()


def test_sync_product_no_product(
    mocker, expected_account, product_new_file, product_data_from_dict
):
    mocker.patch("swo.mpt.cli.core.products.app.get_active_account", return_value=expected_account)
    stats_mock = Mock(spec=ProductStatsCollector, is_error=False, to_table=Mock(return_value=""))
    validate_definition_mock = mocker.patch.object(
        ProductService,
        "validate_definition",
        return_value=ServiceResult(success=True, model=None, stats=stats_mock),
    )
    retrieve_mock = mocker.patch.object(
        ProductService,
        "retrieve",
        return_value=ServiceResult(success=True, model=None, stats=stats_mock),
    )
    create_mock = mocker.patch(
        "swo.mpt.cli.core.products.app.create_product",
        return_value=(stats_mock, product_data_from_dict),
    )

    result = runner.invoke(
        app,
        ["sync", str(product_new_file)],
        input="y\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Do you want to create new product for account" in result.stdout
    validate_definition_mock.assert_called_once()
    retrieve_mock.assert_called_once()
    create_mock.assert_called_once()
    stats_mock.to_table.assert_called_once()


def test_create_product(
    mocker,
    expected_account,
    mpt_client,
    product_new_file,
    product_data_from_dict,
    item_data_from_dict,
    parameter_group_data_from_dict,
    parameters_data_from_dict,
    template_data_from_dict,
):
    stats = ProductStatsCollector()
    create_product_mock = mocker.patch.object(
        ProductService,
        "create",
        return_value=ServiceResult(success=True, model=product_data_from_dict, stats=stats),
    )
    create_item_group_mock = mocker.patch.object(
        ItemGroupService,
        "create",
        return_value=ServiceResult(
            success=True,
            model=None,
            collection=DataCollectionModel(collection={"fake_id": item_data_from_dict}),
            stats=stats,
        ),
    )
    create_parameter_group_mock = mocker.patch.object(
        ParameterGroupService,
        "create",
        return_value=ServiceResult(
            success=True,
            model=None,
            collection=DataCollectionModel(collection={"fake_id": parameters_data_from_dict}),
            stats=stats,
        ),
    )
    create_parameter_service_mock = mocker.patch.object(
        ParametersService,
        "create",
        return_value=ServiceResult(
            success=True,
            model=None,
            collection=DataCollectionModel(collection={"fake_id": parameters_data_from_dict}),
            stats=stats,
        ),
    )
    set_new_parameter_mock = mocker.patch.object(ParametersService, "set_new_parameter_group")
    create_template_service_mock = mocker.patch.object(
        TemplateService,
        "create",
        return_value=ServiceResult(success=True, model=template_data_from_dict, stats=stats),
    )
    set_new_parameter_template_mock = mocker.patch.object(
        TemplateService, "set_new_parameter_group"
    )
    create_item_service_mock = mocker.patch.object(
        ItemService,
        "create",
        return_value=ServiceResult(success=True, model=item_data_from_dict, stats=stats),
    )
    set_new_item_groups_mock = mocker.patch.object(ItemService, "set_new_item_groups")
    add_collection_spy = mocker.spy(DataCollectionModel, "add")

    create_product(expected_account, mpt_client, product_new_file, stats, Mock())

    create_product_mock.assert_called_once()
    create_item_group_mock.assert_called_once()
    create_parameter_group_mock.assert_called_once()
    assert create_parameter_service_mock.call_count == 4
    assert set_new_parameter_mock.call_count == 4
    assert add_collection_spy.call_count == 3
    create_template_service_mock.assert_called_once()
    set_new_parameter_template_mock.assert_called_once()
    create_item_service_mock.assert_called_once()
    set_new_item_groups_mock.assert_called_once()


def test_create_product_error(
    mocker,
    expected_account,
    mpt_client,
    product_new_file,
    product_data_from_dict,
    item_data_from_dict,
    parameter_group_data_from_dict,
    parameters_data_from_dict,
    template_data_from_dict,
):
    stats = ProductStatsCollector()
    create_product_mock = mocker.patch.object(
        ProductService,
        "create",
        return_value=ServiceResult(success=False, model=None, stats=stats),
    )
    create_item_group_spy = mocker.spy(ItemGroupService, "create")
    create_parameter_group_spy = mocker.spy(ParameterGroupService, "create")
    create_parameter_spy = mocker.spy(ParametersService, "create")
    create_template_spy = mocker.spy(TemplateService, "create")
    create_item_spy = mocker.spy(ItemService, "create")

    create_product(expected_account, mpt_client, product_new_file, stats, Mock())

    create_product_mock.assert_called_once()
    create_item_group_spy.assert_not_called()
    create_parameter_group_spy.assert_not_called()
    create_parameter_spy.assert_not_called()
    create_template_spy.assert_not_called()
    create_item_spy.assert_not_called()


def test_create_product_collections_is_empty(
    mocker,
    expected_account,
    mpt_client,
    product_new_file,
    product_data_from_dict,
    item_data_from_dict,
    parameter_group_data_from_dict,
    parameters_data_from_dict,
    template_data_from_dict,
):
    stats = ProductStatsCollector()
    mocker.patch.object(
        ProductService,
        "create",
        return_value=ServiceResult(success=True, model=product_data_from_dict, stats=stats),
    )
    mocker.patch.object(
        ItemGroupService,
        "create",
        return_value=ServiceResult(success=True, model=None, collection=None, stats=stats),
    )
    mocker.patch.object(
        ParameterGroupService,
        "create",
        return_value=ServiceResult(success=True, model=None, collection=None, stats=stats),
    )
    mocker.patch.object(
        ParametersService,
        "create",
        return_value=ServiceResult(success=True, model=None, collection=None, stats=stats),
    )
    set_new_parameter_mock = mocker.patch.object(ParametersService, "set_new_parameter_group")
    mocker.patch.object(
        TemplateService,
        "create",
        return_value=ServiceResult(success=True, model=template_data_from_dict, stats=stats),
    )
    set_new_parameter_template_mock = mocker.patch.object(
        TemplateService, "set_new_parameter_group"
    )
    mocker.patch.object(
        ItemService,
        "create",
        return_value=ServiceResult(success=True, model=item_data_from_dict, stats=stats),
    )
    set_new_item_groups_mock = mocker.patch.object(ItemService, "set_new_item_groups")

    create_product(expected_account, mpt_client, product_new_file, stats, Mock())

    set_new_parameter_mock.assert_not_called()
    set_new_parameter_template_mock.assert_not_called()
    set_new_item_groups_mock.assert_not_called()


def test_update_product(
    mocker,
    expected_account,
    mpt_client,
    product_new_file,
    product_data_from_dict,
    item_data_from_dict,
    parameter_group_data_from_dict,
    parameters_data_from_dict,
    template_data_from_dict,
):
    stats = ProductStatsCollector()
    update_item_service_mock = mocker.patch.object(
        ItemService,
        "update",
        return_value=ServiceResult(success=True, model=item_data_from_dict, stats=stats),
    )

    update_product(
        expected_account, mpt_client, product_new_file, stats, product_data_from_dict, Mock()
    )

    update_item_service_mock.assert_called_once()
