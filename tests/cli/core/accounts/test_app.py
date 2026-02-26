import json
from pathlib import Path

import pytest
import typer
from cli.core.accounts.app import app, get_active_account, protocol_and_host
from cli.core.accounts.handlers import JsonFileHandler
from cli.core.errors import MPTAPIError
from cli.core.mpt.models import Account, Token
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def vendor_token():
    return Token(
        id="TKN-1111-1111",
        account=Account(
            id="ACC-12345new",
            name="New Account",
            type="Vendor",
        ),
        token="idt:TKN-1111-1111:secret",  # noqa: S106
    )


@pytest.fixture
def existing_token_factory():
    def factory(token_value):
        return Token(
            id="TKN-1111-1111",
            account=Account(id="ACC-12342", name="Account 2", type="Vendor"),
            token=token_value,
        )

    return factory


def test_add_account_accounts_file_not_exists(tmp_path, mocker, vendor_token):
    account_file_path = tmp_path / ".swocli" / "accounts.json"
    mocker.patch.object(JsonFileHandler, "_default_file_path", account_file_path)
    mocker.patch(
        "cli.core.accounts.api.account_api_service.MPTAccountService.get_authentication",
        return_value=vendor_token,
        autospec=True,
    )

    result = runner.invoke(app, ["add", "idt:TKN-1111-1111:secret"])

    assert result.exit_code == 0, result.stdout
    with Path(account_file_path).open(encoding="utf-8") as opened_file:
        loaded_accounts = json.load(opened_file)
    assert loaded_accounts == [
        {
            "id": "ACC-12345new",
            "name": "New Account",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://api.platform.softwareone.com",
            "is_active": True,
        }
    ]


def test_add_account_accounts_file_exists(new_accounts_path, mocker, vendor_token):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch(
        "cli.core.accounts.api.account_api_service.MPTAccountService.get_authentication",
        return_value=vendor_token,
        autospec=True,
    )

    result = runner.invoke(app, ["add", "idt:TKN-1111-1111:secret"])

    assert result.exit_code == 0, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as opened_file:
        loaded_accounts = json.load(opened_file)
    assert loaded_accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-1111-1112:secret2",
            "token_id": "TKN-1111-1112",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12345new",
            "name": "New Account",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://api.platform.softwareone.com",
            "is_active": True,
        },
    ]


def test_add_account_override_environment(new_accounts_path, mocker, vendor_token):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch(
        "cli.core.accounts.api.account_api_service.MPTAccountService.get_authentication",
        return_value=vendor_token,
        autospec=True,
    )

    result = runner.invoke(
        app,
        [
            "add",
            "idt:TKN-1111-1111:secret",
            "--environment",
            "https://new-environment.example.com",
        ],
    )

    assert result.exit_code == 0, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as opened_file:
        loaded_accounts = json.load(opened_file)
    assert loaded_accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-1111-1112:secret2",
            "token_id": "TKN-1111-1112",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12345new",
            "name": "New Account",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://new-environment.example.com",
            "is_active": True,
        },
    ]


def test_add_account_token_failed(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch(
        "cli.core.accounts.api.account_api_service.MPTAccountService.get_authentication",
        side_effect=MPTAPIError("critical error", "you can't perform the operation"),
        autospec=True,
    )

    result = runner.invoke(app, ["add", "idt:TKN-1111-1111:secret"])

    assert result.exit_code == 3, result.stdout


def test_add_existing_account_do_not_replace(new_accounts_path, mocker, existing_token_factory):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch(
        "cli.core.accounts.api.account_api_service.MPTAccountService.get_authentication",
        return_value=existing_token_factory("idt:TKN-1111-1111:secret"),
        autospec=True,
    )

    result = runner.invoke(app, ["add", "idt:TKN-1111-1111:secret"], input="N\n")

    assert result.exit_code == 1, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as opened_file:
        loaded_accounts = json.load(opened_file)
    assert loaded_accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://example.com",
            "is_active": True,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-1111-1112:secret2",
            "token_id": "TKN-1111-1112",
            "environment": "https://example.com",
            "is_active": False,
        },
    ]


def test_add_existing_account_replace(new_accounts_path, mocker, existing_token_factory):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch(
        "cli.core.accounts.api.account_api_service.MPTAccountService.get_authentication",
        return_value=existing_token_factory("idt:TKN-1111-1111:secret"),
        autospec=True,
    )

    result = runner.invoke(app, ["add", "idt:TKN-1111-1111:secret"], input="y\n")

    assert result.exit_code == 0, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as opened_file:
        loaded_accounts = json.load(opened_file)
    assert loaded_accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://api.platform.softwareone.com",
            "is_active": True,
        },
    ]


def test_activate_account_file_not_exists(tmp_path, mocker):
    account_file_path = tmp_path / ".swocli" / "accounts.json"
    mocker.patch.object(JsonFileHandler, "_default_file_path", account_file_path)

    result = runner.invoke(app, ["activate", "ACC-12345"])

    assert result.exit_code == 3, result.stdout


def test_activate_account_doesnot_exist(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    result = runner.invoke(app, ["activate", "ACC-not-exists"])

    assert result.exit_code == 3, result.stdout


def test_activate_account(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    result = runner.invoke(app, ["activate", "ACC-12342"])

    assert result.exit_code == 0, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as opened_file:
        loaded_accounts = json.load(opened_file)
    assert loaded_accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "idt:TKN-1111-1111:secret",
            "token_id": "TKN-1111-1111",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-1111-1112:secret2",
            "token_id": "TKN-1111-1112",
            "environment": "https://example.com",
            "is_active": True,
        },
    ]


def test_remove_accounts_file_not_exists(tmp_path, mocker):
    account_file_path = tmp_path / ".swocli" / "accounts.json"
    mocker.patch.object(JsonFileHandler, "_default_file_path", account_file_path)

    result = runner.invoke(app, ["remove", "ACC-12345"])

    assert result.exit_code == 3, result.stdout


def test_remove_account_doesnot_exist(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    result = runner.invoke(app, ["remove", "ACC-not-exists"])

    assert result.exit_code == 3, result.stdout


def test_remove_account_donot_remove(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    result = runner.invoke(app, ["remove", "ACC-12341"], input="N\n")

    assert result.exit_code == 1, result.stdout


def test_remove_account(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    result = runner.invoke(app, ["remove", "ACC-12341"], input="y\n")

    assert result.exit_code == 0, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as opened_file:
        loaded_accounts = json.load(opened_file)
    assert loaded_accounts == [
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-1111-1112:secret2",
            "token_id": "TKN-1111-1112",
            "environment": "https://example.com",
            "is_active": False,
        }
    ]


def test_list_accounts_accounts_file_not_exists(tmp_path, mocker):
    account_file_path = tmp_path / ".swocli" / "accounts.json"
    mocker.patch.object(JsonFileHandler, "_default_file_path", account_file_path)

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0, result.stdout


def test_list_accounts(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0, result.stdout
    assert all((account in result.stdout) for account in ["ACC-12341", "ACC-12342"]), result.stdout


def test_list_active_account(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    result = runner.invoke(app, ["list", "--active"])

    assert result.exit_code == 0, result.stdout
    assert "ACC-12341" in result.stdout
    assert "ACC-12342" not in result.stdout


def test_get_active_account(new_accounts_path, mocker, active_vendor_account):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    result = get_active_account()

    assert result == active_vendor_account


def test_get_active_account_no_active_account(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    with Path(new_accounts_path).open(encoding="utf-8") as opened_file:
        loaded_accounts = json.load(opened_file)
    loaded_accounts = [{**account_record, "is_active": False} for account_record in loaded_accounts]
    with Path(new_accounts_path).open("w", encoding="utf-8") as opened_file:
        json.dump(loaded_accounts, opened_file)

    with pytest.raises(typer.Exit):
        get_active_account()


@pytest.mark.parametrize(
    ("input_url", "expected"),
    [
        ("//[2001:db8:85a3::8a2e:370:7334]:80/a", "https://[2001:db8:85a3::8a2e:370:7334]:80/a"),
        ("//example.com", "https://example.com"),
        ("http://example.com", "http://example.com"),
        ("http://example.com:88/something/else", "http://example.com:88/something/else"),
        ("http://user@example.com:88/", "http://example.com:88"),
        ("http://user:pass@example.com:88/", "http://example.com:88"),
        ("http://example.com/public", "http://example.com"),
        ("http://example.com/public/", "http://example.com"),
        ("http://example.com/public/else", "http://example.com/public/else"),
        ("http://example.com/public/v1", "http://example.com"),
        ("http://example.com/public/v1/", "http://example.com"),
        ("http://example.com/else/public", "http://example.com/else/public"),
        ("http://example.com/elsepublic", "http://example.com/elsepublic"),
    ],
)
def test_protocol_and_host(input_url, expected):
    result = protocol_and_host(input_url)

    assert result == expected


@pytest.mark.parametrize(
    "input_url",
    [
        "http//example.com",
        "://example.com",
        "http:example.com",
        "http:/example.com",
    ],
)
def test_protocol_and_host_error(input_url):
    with pytest.raises(ValueError):
        protocol_and_host(input_url)
