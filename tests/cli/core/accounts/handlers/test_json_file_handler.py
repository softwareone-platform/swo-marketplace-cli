import json
from pathlib import Path

import pytest
from cli.core.accounts.handlers.json_file_handler import JsonFileHandler


@pytest.fixture
def json_handler(tmp_path):
    return JsonFileHandler(file_path=tmp_path / "fake_accounts.json")


def test_read_existing_file(mocker, json_handler):
    mocker.patch.object(json_handler, "exists", return_value=True)
    mock_open = mocker.patch.object(
        Path, "open", mocker.mock_open(read_data=json.dumps([{"key": "value"}]))
    )

    result = json_handler.read()

    assert result == [{"key": "value"}]
    mock_open.assert_called_once()
    mock_open().read.assert_called_once()


def test_read_creates_empty_file_when_nonexistent(mocker, json_handler):
    mocker.patch.object(json_handler, "exists", return_value=False, autospec=True)
    mock_create = mocker.patch.object(json_handler, "create", autospec=True)
    mocker.patch.object(Path, "open", mocker.mock_open(read_data="[]"))

    result = json_handler.read()

    assert result == []
    mock_create.assert_called_once()


def test_write_creates_directory_if_not_exists(tmp_path):
    expected_records = [{"id": "test_id", "name": "Test Name"}]
    nonexistent_dir = tmp_path / "nonexistent_dir"
    target_file_path = nonexistent_dir / "accounts.json"
    json_handler = JsonFileHandler(file_path=target_file_path)

    json_handler.write(expected_records)  # act

    assert nonexistent_dir.exists()
    assert target_file_path.exists()
    with Path(target_file_path).open(encoding="utf-8") as opened_file:
        loaded_content = json.load(opened_file)
    assert loaded_content == expected_records


def test_write_writes_correct_data_to_file(json_handler):
    expected_records = [{"id": "test_id", "name": "Test Name"}]

    json_handler.write(expected_records)  # act

    with Path(json_handler.file_path).open(encoding="utf-8") as opened_file:
        loaded_content = json.load(opened_file)
    assert loaded_content == expected_records


def test_write_add_data_to_existing_file(json_handler):
    initial_records = [{"id": "initial_id", "name": "Initial Name"}]
    updated_records = [{"id": "updated_id", "name": "Updated Name"}]
    json_handler.write(initial_records)

    json_handler.write(updated_records)  # act

    with Path(json_handler.file_path).open(encoding="utf-8") as opened_file:
        loaded_content = json.load(opened_file)
    assert loaded_content == updated_records


def test_write_empty_data(json_handler):
    empty_records = []

    json_handler.write(empty_records)  # act

    with Path(json_handler.file_path).open(encoding="utf-8") as opened_file:
        loaded_content = json.load(opened_file)
    assert loaded_content == empty_records
