import pytest
from cli.core.accounts.models import Account
from cli.core.accounts.table_formatters import wrap_account_type, wrap_active, wrap_token


@pytest.fixture
def account_factory():
    def factory(token, token_id):
        return Account(
            id="ACC-12342",
            name="Account 2",
            type="Vendor",
            token=token,
            token_id=token_id,
            environment="https://example.com",
            is_active=False,
        )

    return factory


@pytest.mark.parametrize(
    ("account_type", "expected"),
    [
        ("Vendor", "[cyan]Vendor"),
        ("Operations", "[white]Operations"),
        ("Client", "[magenta]Client"),
        ("Other", "Other"),
    ],
)
def test_wrap_account_type(account_type, expected):
    result = wrap_account_type(account_type)

    assert result == expected


@pytest.mark.parametrize(("is_active", "expected"), [(True, "[red bold]\u2714"), (False, "")])
def test_wrap_active(is_active, expected):
    result = wrap_active(is_active=is_active)

    assert result == expected


@pytest.mark.parametrize(
    ("token", "token_id", "to_wrap_secret", "expected"),
    [
        (
            "idt:TKN-1111-1111:secret",
            "TKN-1111-1111",
            True,
            "idt:TKN-1111-1111:secr*****idt:",
        ),
        (
            "tokensecret",
            "TKN-2222-2222",
            True,
            "TKN-*****TKN-",
        ),
        (
            "tokensecret",
            "TKN-3333-3333",
            False,
            "TKN-3333-3333:tokensecret",
        ),
    ],
)
def test_wrap_token(account_factory, token, token_id, to_wrap_secret, expected):
    account = account_factory(token, token_id)

    result = wrap_token(account, to_wrap_secret=to_wrap_secret)

    assert result == expected
