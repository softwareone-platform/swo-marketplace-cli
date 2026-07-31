import pytest
from cli.core.accounts.transport import CLITransport


def test_targets_account_environment(active_vendor_account):
    result = CLITransport(account=active_vendor_account)

    assert result.url == active_vendor_account.environment


def test_account_environment_is_sanitized(active_vendor_account):
    active_vendor_account.environment = "https://example.com/public/v1"

    result = CLITransport(account=active_vendor_account)

    assert result.url == "https://example.com"


def test_explicit_base_url_wins_over_account(active_vendor_account):
    result = CLITransport(base_url="https://api.elsewhere.com", account=active_vendor_account)

    assert result.url == "https://api.elsewhere.com"


def test_no_base_url_and_no_account_raises_error():
    with pytest.raises(ValueError, match="Base URL is required"):
        CLITransport()


def test_default_timeout_matches_from_config(active_vendor_account):
    result = CLITransport(account=active_vendor_account)

    assert result.timeout == pytest.approx(60.0)
