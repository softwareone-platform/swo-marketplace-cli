from swo.mpt.cli.core.products.models.product import ProductData


def test_product_data_from_dict(product_file_data):
    result = ProductData.from_dict(product_file_data)

    assert result.id == "PRD-1234-1234-1234"
    assert result.coordinate == "B3"
    assert result.name == "Test Product Name"
    assert result.short_description == "Catalog description"
    assert result.long_description == "Product description"
    assert result.website == "https://example.com"


def test_product_data_to_json(product_data_from_dict):
    result = product_data_from_dict.to_json()

    assert result["name"] == "Adobe Commerce (CLI Test)"
    assert result["shortDescription"] == "Catalog description"
    assert result["website"] == "https://example.com"
