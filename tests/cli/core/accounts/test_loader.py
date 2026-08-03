import json

import pytest
from cli.core.accounts.loader import load_account
from cli.core.errors import AccountNotFoundError, CLIAccountError, NoActiveAccountFoundError


def test_selects_active_account(write_accounts, active_vendor_account, inactive_vendor_account):
    file_path = write_accounts([inactive_vendor_account, active_vendor_account])

    result = load_account(file_path)

    assert result == active_vendor_account


def test_selects_account_by_id(write_accounts, active_vendor_account, inactive_vendor_account):
    file_path = write_accounts([active_vendor_account, inactive_vendor_account])

    result = load_account(file_path, account_id="ACC-12342")

    assert result == inactive_vendor_account


def test_unknown_account_id_raises_error(write_accounts, active_vendor_account):
    file_path = write_accounts([active_vendor_account])

    with pytest.raises(AccountNotFoundError, match="ACC-99999"):
        load_account(file_path, account_id="ACC-99999")


def test_file_missing_raises_error(account_file_path):
    with pytest.raises(CLIAccountError, match="not found"):
        load_account(account_file_path)


def test_file_missing_does_not_create_file(account_file_path):
    with pytest.raises(CLIAccountError):
        load_account(account_file_path)

    assert not account_file_path.exists()


def test_invalid_json_raises_error(account_file_path):
    account_file_path.parent.mkdir(parents=True, exist_ok=True)
    account_file_path.write_text("not-json{")

    with pytest.raises(CLIAccountError, match="not valid JSON"):
        load_account(account_file_path)


def test_non_list_payload_raises_error(account_file_path):
    account_file_path.parent.mkdir(parents=True, exist_ok=True)
    account_file_path.write_text(json.dumps({"id": "ACC-12341"}))

    with pytest.raises(CLIAccountError, match="JSON list"):
        load_account(account_file_path)


def test_no_active_account_raises_error(write_accounts, inactive_vendor_account):
    file_path = write_accounts([inactive_vendor_account])

    with pytest.raises(NoActiveAccountFoundError):
        load_account(file_path)


@pytest.mark.parametrize("missing_field", ["token", "environment"])
def test_missing_required_field_raises_error(
    write_accounts_file, active_vendor_account, missing_field
):
    raw_account = active_vendor_account.model_dump()
    raw_account.pop(missing_field)
    file_path = write_accounts_file([raw_account])

    with pytest.raises(CLIAccountError, match="invalid account") as error_info:
        load_account(file_path)

    assert "secret" not in str(error_info.value)


def test_unknown_extra_fields_are_tolerated(write_accounts_file, active_vendor_account):
    raw_account = {**active_vendor_account.model_dump(), "extra": "field"}
    file_path = write_accounts_file([raw_account])

    result = load_account(file_path)

    assert result == active_vendor_account


def test_default_path_reads_home_swocli(
    default_accounts_path, write_accounts, active_vendor_account
):
    write_accounts([active_vendor_account])

    result = load_account()

    assert result == active_vendor_account
