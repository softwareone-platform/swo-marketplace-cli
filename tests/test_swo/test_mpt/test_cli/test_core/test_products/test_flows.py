from pathlib import Path

import pytest
from swo.mpt.cli.core.errors import FileNotExistsError
from swo.mpt.cli.core.products.flows import (
    check_file_exists,
    check_product_definition,
    get_definition_file,
)
from swo.mpt.cli.core.stats import StatsCollector


def test_get_definition_file():
    file_path = "/example/PRD-1234-1234.xlsx"

    assert get_definition_file(file_path) == Path(file_path)


def test_get_definition_file_add_postfix():
    file_path = "/example/PRD-1234-1234"

    assert get_definition_file(file_path) == Path(f"{file_path}.xlsx")


def test_check_file_exists(empty_file):
    assert check_file_exists(empty_file)


def test_check_file_not_exists(tmp_path):
    with pytest.raises(FileNotExistsError):
        check_file_exists("tmp_path")


def test_check_product_definition_not_all_tabs(empty_file):
    stats = StatsCollector()

    stats = check_product_definition(empty_file, stats)

    expected_message = """General: Required tab doesn't exist
Parameters Groups: Required tab doesn't exist
Items Groups: Required tab doesn't exist
Agreements Parameters: Required tab doesn't exist
Item Parameters: Required tab doesn't exist
Request Parameters: Required tab doesn't exist
Subscription Parameters: Required tab doesn't exist
Items: Required tab doesn't exist
Templates: Required tab doesn't exist
Settings: Required tab doesn't exist\n"""

    assert not stats.is_empty()
    assert str(stats) == expected_message


def test_check_product_definition_not_all_required_general(product_file_root):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root / "PRD-1234-1234-1234-general-not-all.xlsx", stats
    )

    assert not stats.is_empty()
    assert (
        str(stats)
        == """General: Required field Product Name is not provided
\t\tProduct Website: Value is not provided for the required field. Current value: None"""
    )


def test_check_product_definition_not_all_required_parameter_groups(product_file_root):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root / "PRD-1234-1234-1234-parameter-groups-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert str(stats) == "Parameters Groups: Required field Label is not provided\n"


def test_check_product_definition_not_all_required_items_groups(product_file_root):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root / "PRD-1234-1234-1234-items-groups-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert str(stats) == "Items Groups: Required field Label is not provided\n"


def test_check_product_definition_not_all_required_agreements_parameters(
    product_file_root,
):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root
        / "PRD-1234-1234-1234-agreements-parameters-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert (
        str(stats)
        == "Agreements Parameters: Required field ExternalId is not provided\n"
    )


def test_check_product_definition_not_all_required_item_parameters(
    product_file_root,
):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root / "PRD-1234-1234-1234-item-parameters-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert str(stats) == "Item Parameters: Required field ExternalId is not provided\n"


def test_check_product_definition_not_all_required_request_parameters(
    product_file_root,
):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root
        / "PRD-1234-1234-1234-request-parameters-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert (
        str(stats) == "Request Parameters: Required field ExternalId is not provided\n"
    )


def test_check_product_definition_not_all_required_subscription_parameters(
    product_file_root,
):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root
        / "PRD-1234-1234-1234-subscription-parameters-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert (
        str(stats)
        == "Subscription Parameters: Required field ExternalId is not provided\n"
    )


def test_check_product_definition_not_all_required_items(
    product_file_root,
):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root / "PRD-1234-1234-1234-items-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert str(stats) == "Items: Required field Billing Frequency is not provided\n"


def test_check_product_definition_not_all_required_templates(
    product_file_root,
):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root / "PRD-1234-1234-1234-templates-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert str(stats) == "Templates: Required field Content is not provided\n"


def test_check_product_definition_not_all_required_settings(
    product_file_root,
):
    stats = StatsCollector()

    stats = check_product_definition(
        product_file_root / "PRD-1234-1234-1234-settings-not-all-columns.xlsx",
        stats,
    )

    assert not stats.is_empty()
    assert str(stats) == "Settings: Required field Value is not provided\n"
