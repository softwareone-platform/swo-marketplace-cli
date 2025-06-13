from pathlib import Path

import pytest
from swo.mpt.cli.core.handlers import FileHandler


class FakeFileHandler(FileHandler):
    def create(self):
        pass

    def read(self):
        return "fake"

    def write(self, data):
        pass


@pytest.fixture
def test_exists_file_returns_true(mocker):
    mocker.patch("os.path.exists", return_value=True)

    file_handler = FakeFileHandler(Path("test.txt"))

    assert file_handler.exists() is True


@pytest.fixture
def test_exists_file_returns_false(mocker):
    mocker.patch("os.path.exists", return_value=False)

    file_handler = FakeFileHandler(Path("test.txt"))

    assert file_handler.exists() is False
