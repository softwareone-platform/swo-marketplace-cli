from cli.core.models import DataCollectionModel
from cli.core.products import app as product_app
from cli.core.services.service_result import ServiceResult
from cli.core.stats import ProductStatsCollector
from typer.testing import CliRunner

runner = CliRunner()


def _stub_product_service(mocker, product_container_mock, product_data_from_dict):
    """Set up the product service mock with validate_definition + retrieve."""
    product_container_mock.product_service().validate_definition.return_value = ServiceResult(
        success=True, model=None, stats=mocker.Mock()
    )
    product_container_mock.product_service().retrieve.return_value = ServiceResult(
        success=True, model=product_data_from_dict, stats=mocker.Mock()
    )


def _stub_service_create(mocker, service_mock, collection_data):
    """Set up a service create() mock with a DataCollectionModel collection."""
    service_mock.create.return_value = ServiceResult(
        success=True,
        model=None,
        collection=DataCollectionModel(collection={"fake_id": collection_data}),
        stats=mocker.Mock(),
    )


def test_sync_not_valid_definition(mocker, product_container_mock):
    product_container_mock.product_service().validate_definition.return_value = ServiceResult(
        success=False, model=None, stats=mocker.Mock()
    )

    result = runner.invoke(product_app, ["sync", "--dry-run", "some-file"])

    assert result.exit_code == 3, result.stdout


def test_sync_with_dry_run(mocker, product_container_mock):
    product_container_mock.product_service().validate_definition.return_value = ServiceResult(
        success=True, model=None, stats=mocker.Mock()
    )

    result = runner.invoke(product_app, ["sync", "--dry-run", "fake_file.xlsx"])

    assert result.exit_code == 0, result.stdout
    assert "Product definition" in result.stdout
    product_container_mock.product_service().create.assert_not_called()
    product_container_mock.product_service().update.assert_not_called()


def test_sync_product_update_runs_update_flow(
    mocker, product_container_mock, product_data_from_dict
):
    mocker.patch.object(ProductStatsCollector, "has_errors", new=False)
    mocker.patch("cli.core.products.app.sync.stats_table_renderer.render", return_value="")
    _stub_product_service(mocker, product_container_mock, product_data_from_dict)

    result = runner.invoke(product_app, ["sync", "fake_file.xlsx"], input="y\n")

    assert result.exit_code == 0, result.stdout
    assert "Do you want to update product" in result.stdout
    product_container_mock.product_service().update.assert_called_once()
    product_container_mock.item_service().update.assert_called_once()
    product_container_mock.item_group_service().update.assert_called_once()
    product_container_mock.template_service().update.assert_called_once()
    product_container_mock.parameter_group_service().update.assert_called_once()
    product_container_mock.agreement_parameters_service().update.assert_called_once()
    product_container_mock.asset_parameters_service().update.assert_called_once()
    product_container_mock.item_parameters_service().update.assert_called_once()
    product_container_mock.request_parameters_service().update.assert_called_once()
    product_container_mock.subscription_parameters_service().update.assert_called_once()


def test_sync_product_update_with_errors(mocker, product_container_mock, product_data_from_dict):
    mocker.patch.object(ProductStatsCollector, "has_errors", new=True)
    _stub_product_service(mocker, product_container_mock, product_data_from_dict)

    result = runner.invoke(product_app, ["sync", "fake_file.xlsx"], input="y\n")

    assert result.exit_code == 3, result.stdout
    product_container_mock.product_service().update.assert_called_once()


def test_sync_product_force_create_runs(
    mocker, product_container_mock, product_new_file, product_data_from_dict, product_related_data
):
    mocker.patch.object(ProductStatsCollector, "has_errors", new=False)
    render_mock = mocker.patch(
        "cli.core.products.app.sync.stats_table_renderer.render", return_value=""
    )
    _stub_product_service(mocker, product_container_mock, product_data_from_dict)
    product_container_mock.product_service().create.return_value = ServiceResult(
        success=True, model=product_data_from_dict, stats=mocker.Mock()
    )
    _stub_service_create(
        mocker, product_container_mock.item_group_service(), product_related_data["item_group"]
    )
    _stub_service_create(
        mocker,
        product_container_mock.parameter_group_service(),
        product_related_data["parameter_group"],
    )
    for parameter_service in (
        product_container_mock.agreement_parameters_service(),
        product_container_mock.asset_parameters_service(),
        product_container_mock.item_parameters_service(),
        product_container_mock.request_parameters_service(),
        product_container_mock.subscription_parameters_service(),
    ):
        _stub_service_create(mocker, parameter_service, product_related_data["parameters"])

    result = runner.invoke(
        product_app,
        ["sync", "--force-create", str(product_new_file)],
        input="y\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Do you want to create new" in result.stdout
    product_container_mock.product_service().create.assert_called_once()
    product_container_mock.item_service().create.assert_called_once()
    product_container_mock.template_service().create.assert_called_once()
    render_mock.assert_called_once()


def test_sync_product_no_product_runs_create_flow(
    mocker, product_new_file, product_container_mock, product_related_data
):
    mocker.patch.object(ProductStatsCollector, "has_errors", new=False)
    render_mock = mocker.patch(
        "cli.core.products.app.sync.stats_table_renderer.render", return_value=""
    )
    product_container_mock.product_service().validate_definition.return_value = ServiceResult(
        success=True, model=None, stats=mocker.Mock()
    )
    product_container_mock.product_service().retrieve.return_value = ServiceResult(
        success=True, model=None, stats=mocker.Mock()
    )
    product_container_mock.product_service().create.return_value = ServiceResult(
        success=True, model=product_related_data["template"], stats=mocker.Mock()
    )
    _stub_service_create(
        mocker, product_container_mock.item_group_service(), product_related_data["item_group"]
    )
    _stub_service_create(
        mocker,
        product_container_mock.parameter_group_service(),
        product_related_data["parameter_group"],
    )
    for parameter_service in (
        product_container_mock.agreement_parameters_service(),
        product_container_mock.asset_parameters_service(),
        product_container_mock.item_parameters_service(),
        product_container_mock.request_parameters_service(),
        product_container_mock.subscription_parameters_service(),
    ):
        _stub_service_create(mocker, parameter_service, product_related_data["parameters"])
    add_collection_spy = mocker.spy(DataCollectionModel, "add")

    result = runner.invoke(product_app, ["sync", str(product_new_file)], input="y\n")

    assert result.exit_code == 0, result.stdout
    assert "Do you want to create new product for account" in result.stdout
    product_container_mock.product_service().create.assert_called_once()
    product_container_mock.item_service().create.assert_called_once()
    product_container_mock.template_service().create.assert_called_once()
    assert add_collection_spy.call_count == 4
    render_mock.assert_called_once()


def test_sync_aborts_when_product_create_fails(mocker, product_new_file, product_container_mock):
    mocker.patch.object(ProductStatsCollector, "has_errors", new=False)
    mocker.patch("cli.core.products.app.sync.stats_table_renderer.render", return_value="")
    product_container_mock.product_service().validate_definition.return_value = ServiceResult(
        success=True, model=None, stats=mocker.Mock()
    )
    product_container_mock.product_service().retrieve.return_value = ServiceResult(
        success=True, model=None, stats=mocker.Mock()
    )
    product_container_mock.product_service().create.return_value = ServiceResult(
        success=False, model=None, stats=mocker.Mock()
    )

    result = runner.invoke(product_app, ["sync", str(product_new_file)], input="y\n")

    assert result.exit_code == 0, result.stdout
    product_container_mock.product_service().create.assert_called_once()
    product_container_mock.item_service().create.assert_not_called()
    product_container_mock.item_group_service().create.assert_not_called()
