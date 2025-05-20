import json
import os

import pytest
from swo.mpt.cli.core.accounts.handlers.json_file_handler import JsonFileHandler


@pytest.fixture
def mock_file_path(tmp_path):
    return tmp_path / "fake_accounts.json"


@pytest.fixture
def json_file_handler(mock_file_path):
    return JsonFileHandler(file_path=mock_file_path)


@pytest.fixture
def mock_config_data():
    return {"key": "value"}


def test_read_existing_file(mocker, json_file_handler, mock_config_data):
    mocker.patch.object(json_file_handler, "exists", return_value=True)
    mock_open = mocker.patch(
        "builtins.open", mocker.mock_open(read_data=json.dumps(mock_config_data))
    )

    data = json_file_handler.read()

    assert data == mock_config_data
    mock_open.assert_called_once_with(json_file_handler.file_path)
    mock_open().read.assert_called_once()


def test_read_creates_empty_file_when_nonexistent(mocker, json_file_handler):
    mocker.patch.object(json_file_handler, "exists", return_value=False)
    mock_create_empty = mocker.patch.object(json_file_handler, "_create_empty_file")
    mocker.patch("builtins.open", mocker.mock_open(read_data="[]"))

    data = json_file_handler.read()

    assert data == []
    mock_create_empty.assert_called_once()


def test_write_creates_directory_if_not_exists(mocker, tmp_path):
    data = [{"id": "test_id", "name": "Test Name"}]
    file_path = tmp_path / "nonexistent_dir" / "accounts.json"
    handler = JsonFileHandler(file_path=file_path)
    mocker.spy(os, "makedirs")

    handler.write(data)

    os.makedirs.assert_called_once_with(str(file_path.parent), exist_ok=True)
    assert file_path.exists()

    with open(file_path) as f:
        file_content = json.load(f)
    assert file_content == data


def test_write_writes_correct_data_to_file(json_file_handler, mock_file_path):
    data = [{"id": "test_id", "name": "Test Name"}]

    json_file_handler.write(data)

    with open(mock_file_path) as f:
        file_content = json.load(f)
    assert file_content == data


def test_write_add_data_to_existing_file(json_file_handler, mock_file_path):
    initial_data = [{"id": "initial_id", "name": "Initial Name"}]
    updated_data = [{"id": "updated_id", "name": "Updated Name"}]
    with open(mock_file_path, "w") as f:
        json.dump(initial_data, f)

    json_file_handler.write(updated_data)

    with open(mock_file_path) as f:
        file_content = json.load(f)
    assert file_content == updated_data


def test_write_empty_data(json_file_handler, mock_file_path):
    empty_data = []

    json_file_handler.write(empty_data)

    with open(mock_file_path) as f:
        file_content = json.load(f)
    assert file_content == empty_data
