import json
from pathlib import Path

import pytest
from cli.core.accounts.handlers.json_file_handler import JsonFileHandler


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
    mock_open = mocker.patch.object(
        Path, "open", mocker.mock_open(read_data=json.dumps(mock_config_data))
    )

    result = json_file_handler.read()

    assert result == mock_config_data
    mock_open.assert_called_once()
    mock_open().read.assert_called_once()


def test_read_creates_empty_file_when_nonexistent(mocker, json_file_handler):
    mocker.patch.object(json_file_handler, "exists", return_value=False)
    mock_create = mocker.patch.object(json_file_handler, "create")
    mocker.patch.object(Path, "open", mocker.mock_open(read_data="[]"))

    result = json_file_handler.read()

    assert result == []
    mock_create.assert_called_once()


def test_write_creates_directory_if_not_exists(tmp_path):
    expected_records = [{"id": "test_id", "name": "Test Name"}]
    no_existing_dir = tmp_path / "nonexistent_dir"
    file_path = no_existing_dir / "accounts.json"
    json_handler = JsonFileHandler(file_path=file_path)

    json_handler.write(expected_records)  # act

    assert no_existing_dir.exists()
    assert file_path.exists()
    with Path(file_path).open(encoding="utf-8") as file_obj:
        file_content = json.load(file_obj)
    assert file_content == expected_records


def test_write_writes_correct_data_to_file(json_file_handler, mock_file_path):
    expected_records = [{"id": "test_id", "name": "Test Name"}]

    json_file_handler.write(expected_records)  # act

    with Path(mock_file_path).open(encoding="utf-8") as file_obj:
        file_content = json.load(file_obj)
    assert file_content == expected_records


def test_write_add_data_to_existing_file(json_file_handler, mock_file_path):
    initial_data = [{"id": "initial_id", "name": "Initial Name"}]
    updated_data = [{"id": "updated_id", "name": "Updated Name"}]
    with Path(mock_file_path).open("w", encoding="utf-8") as file_obj:
        json.dump(initial_data, file_obj)

    json_file_handler.write(updated_data)  # act

    with Path(mock_file_path).open(encoding="utf-8") as file_obj:
        file_content = json.load(file_obj)
    assert file_content == updated_data


def test_write_empty_data(json_file_handler, mock_file_path):
    empty_data = []

    json_file_handler.write(empty_data)  # act

    with Path(mock_file_path).open(encoding="utf-8") as file_obj:
        file_content = json.load(file_obj)
    assert file_content == empty_data
