import os

from swo.mpt.cli.core.pricelists import app
from swo.mpt.cli.core.stats import PricelistStatsCollector
from typer.testing import CliRunner

runner = CliRunner()


def test_sync_pricelists_not_files_found(pricelist_new_file):
    result = runner.invoke(app, ["sync", "some-file.xlsx"])

    assert result.exit_code == 3, result.stdout
    assert "No files found for provided paths" in result.stdout


def test_sync_pricelists_particular_file(
    mocker, pricelist, pricelist_new_file, expected_account
):
    stats = PricelistStatsCollector()
    sync_pricelist = mocker.patch(
        "swo.mpt.cli.core.pricelists.app.sync_pricelist",
        return_value=(stats, pricelist),
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.get_active_account",
        return_value=expected_account,
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.check_pricelist",
        return_value=pricelist,
    )

    result = runner.invoke(
        app, ["sync", str(pricelist_new_file)], input="y\ny\n"
    )
    assert result.exit_code == 0, result.stdout
    sync_pricelist.assert_called_once()


def test_sync_pricelists_particular_dicrectory(
    mocker, pricelist, pricelist_new_file, expected_account
):
    stats = PricelistStatsCollector()
    sync_pricelist = mocker.patch(
        "swo.mpt.cli.core.pricelists.app.sync_pricelist",
        return_value=(stats, pricelist),
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.get_active_account",
        return_value=expected_account,
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.check_pricelist",
        return_value=pricelist,
    )

    result = runner.invoke(
        app,
        ["sync", os.path.dirname(pricelist_new_file)],
        input="y\ny\n",
    )
    assert result.exit_code == 0, result.stdout
    sync_pricelist.assert_called_once()


def test_sync_pricelists_create_file(
    mocker, pricelist, pricelist_new_file, expected_account
):
    stats = PricelistStatsCollector()
    sync_pricelist = mocker.patch(
        "swo.mpt.cli.core.pricelists.app.sync_pricelist",
        return_value=(stats, pricelist),
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.get_active_account",
        return_value=expected_account,
    )
    mocker.patch(
        "swo.mpt.cli.core.pricelists.app.check_pricelist",
        return_value=None,
    )

    result = runner.invoke(
        app, ["sync", str(pricelist_new_file)], input="y\ny\n"
    )
    assert result.exit_code == 0, result.stdout
    sync_pricelist.assert_called_once()
