import json
from pathlib import Path

import pytest
import typer
from cli.core.accounts import app
from cli.core.accounts.app import get_active_account
from cli.core.accounts.handlers import JsonFileHandler
from cli.core.errors import MPTAPIError
from cli.core.mpt.models import Account, Token
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def new_token():
    return Token(
        id="TKN-123456",
        account=Account(
            id="ACC-12345new",
            name="New Account",
            type="Vendor",
        ),
        token="new-secret",  # noqa: S106
    )


@pytest.fixture
def existing_token():
    def _wrapper(token):
        return Token(
            id="TKN-0000-0000-0002",
            account=Account(
                id="ACC-12342",
                name="Account 2",
                type="Vendor",
            ),
            token=token,
        )

    return _wrapper


def test_add_account_accounts_file_not_exists(tmp_path, mocker, new_token):
    account_file_path = tmp_path / ".swocli" / "accounts.json"
    mocker.patch.object(JsonFileHandler, "_default_file_path", account_file_path)
    mocker.patch("cli.core.accounts.app.get_token", return_value=new_token)

    result = runner.invoke(app, ["add", "new-secret"])

    assert result.exit_code == 0, result.stdout
    with Path(account_file_path).open(encoding="utf-8") as f:
        accounts = json.load(f)

    assert accounts == [
        {
            "id": "ACC-12345new",
            "name": "New Account",
            "type": "Vendor",
            "token": "new-secret",
            "token_id": "TKN-123456",
            "environment": "https://api.platform.softwareone.com/public/v1",
            "is_active": True,
        }
    ]


def test_add_account_accounts_file_exists(new_accounts_path, mocker, new_token):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch("cli.core.accounts.app.get_token", return_value=new_token)

    result = runner.invoke(app, ["add", "new-secret"])

    assert result.exit_code == 0, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as f:
        accounts = json.load(f)

    assert accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "secret 1",
            "token_id": "TKN-0000-0000-0001",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-0000-0000-0002:secret 2",
            "token_id": "TKN-0000-0000-0002",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12345new",
            "name": "New Account",
            "type": "Vendor",
            "token": "new-secret",
            "token_id": "TKN-123456",
            "environment": "https://api.platform.softwareone.com/public/v1",
            "is_active": True,
        },
    ]


def test_add_account_accounts_override_environment(new_accounts_path, mocker, new_token):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch("cli.core.accounts.app.get_token", return_value=new_token)

    result = runner.invoke(
        app,
        [
            "add",
            "new-secret",
            "--environment",
            "https://new-environment.example.com",
        ],
    )

    assert result.exit_code == 0, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as f:
        accounts = json.load(f)

    assert accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "secret 1",
            "token_id": "TKN-0000-0000-0001",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-0000-0000-0002:secret 2",
            "token_id": "TKN-0000-0000-0002",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12345new",
            "name": "New Account",
            "type": "Vendor",
            "token": "new-secret",
            "token_id": "TKN-123456",
            "environment": "https://new-environment.example.com",
            "is_active": True,
        },
    ]


def test_add_account_token_failed(new_accounts_path, mocker):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch(
        "cli.core.accounts.app.get_token",
        side_effect=MPTAPIError("critical error", "you can't perform the operation"),
    )

    result = runner.invoke(app, ["add", "new-secret"])

    assert result.exit_code == 3, result.stdout


def test_add_existing_account_do_not_replace(new_accounts_path, mocker, existing_token):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch("cli.core.accounts.app.get_token", return_value=existing_token("new-super-secret"))

    result = runner.invoke(app, ["add", "new-super-secret"], input="N\n")

    assert result.exit_code == 1, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as f:
        accounts = json.load(f)

    assert accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "secret 1",
            "token_id": "TKN-0000-0000-0001",
            "environment": "https://example.com",
            "is_active": True,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-0000-0000-0002:secret 2",
            "token_id": "TKN-0000-0000-0002",
            "environment": "https://example.com",
            "is_active": False,
        },
    ]


def test_add_existing_account_replace(new_accounts_path, mocker, existing_token):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)
    mocker.patch("cli.core.accounts.app.get_token", return_value=existing_token("new-super-secret"))

    result = runner.invoke(app, ["add", "new-super-secret"], input="y\n")

    assert result.exit_code == 0, result.stdout
    with Path(new_accounts_path).open(encoding="utf-8") as f:
        accounts = json.load(f)

    assert accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "secret 1",
            "token_id": "TKN-0000-0000-0001",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "new-super-secret",
            "token_id": "TKN-0000-0000-0002",
            "environment": "https://api.platform.softwareone.com/public/v1",
            "is_active": True,
        },
    ]


def test_activate_account_accounts_file_not_exists(tmp_path, mocker):
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
    with Path(new_accounts_path).open(encoding="utf-8") as f:
        accounts = json.load(f)

    assert accounts == [
        {
            "id": "ACC-12341",
            "name": "Account 1",
            "type": "Vendor",
            "token": "secret 1",
            "token_id": "TKN-0000-0000-0001",
            "environment": "https://example.com",
            "is_active": False,
        },
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-0000-0000-0002:secret 2",
            "token_id": "TKN-0000-0000-0002",
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
    with Path(new_accounts_path).open(encoding="utf-8") as f:
        accounts = json.load(f)

    assert accounts == [
        {
            "id": "ACC-12342",
            "name": "Account 2",
            "type": "Vendor",
            "token": "idt:TKN-0000-0000-0002:secret 2",
            "token_id": "TKN-0000-0000-0002",
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


def test_get_active_account(new_accounts_path, mocker, expected_account):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    assert get_active_account() == expected_account


def test_get_active_account_no_active_account(new_accounts_path, mocker, expected_account):
    mocker.patch.object(JsonFileHandler, "_default_file_path", new_accounts_path)

    with Path(new_accounts_path).open(encoding="utf-8") as f:
        accounts = json.load(f)

    for account in accounts:
        account["is_active"] = False

    with Path(new_accounts_path).open("w", encoding="utf-8") as f:
        json.dump(accounts, f)

    with pytest.raises(typer.Exit):
        get_active_account()
