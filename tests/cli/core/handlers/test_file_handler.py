from pathlib import Path

import pytest
from cli.core.handlers import FileHandler


class FakeFileHandler(FileHandler):
    def create(self):
        pass

    def read(self):
        return "fake"

    def write(self, records):
        pass


@pytest.mark.parametrize(
    ("exists", "expected_response"),
    [
        (True, True),
        (False, False),
    ],
)
def test_exists_file_returns_true(exists, expected_response, mocker):
    mocker.patch.object(Path, "exists", return_value=exists)

    result = FakeFileHandler(Path("test.txt"))

    assert result.exists() is expected_response
