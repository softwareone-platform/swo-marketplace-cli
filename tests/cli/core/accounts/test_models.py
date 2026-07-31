from cli.core.accounts.models import Account


def test_from_secret_builds_provisional_account():
    result = Account.from_secret("idt:TKN-1111-1111:secret", "https://example.com")

    assert (result.token, result.environment, result.is_active) == (
        "idt:TKN-1111-1111:secret",
        "https://example.com",
        False,
    )


def test_label_combines_id_and_name(active_vendor_account):
    result = active_vendor_account.label

    assert result == f"{active_vendor_account.id} ({active_vendor_account.name})"
