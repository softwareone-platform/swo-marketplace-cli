from cli.core.file_discovery import get_files_path


def test_get_files_path_no_files():
    result = get_files_path(["no_file"])

    assert result == []


def test_get_files_path_single_file(tmp_path):
    file_path = tmp_path / "file.xlsx"
    file_path.touch()

    result = get_files_path([str(file_path)])

    assert len(result) == 1
    assert str(file_path) in result


def test_get_files_path_multiple_files(tmp_path):
    file1 = tmp_path / "file1.xlsx"
    file1.touch()
    file2 = tmp_path / "file2.xlsx"
    file2.touch()

    result = get_files_path([str(file1), str(file2)])

    assert len(result) == 2
    assert str(file1) in result
    assert str(file2) in result


def test_get_files_path_directory(tmp_path):
    file1 = tmp_path / "file.xlsx"
    file1.touch()
    file2 = tmp_path / "file2.xlsx"
    file2.touch()

    result = get_files_path([str(tmp_path)])

    assert len(result) == 2
    assert str(file1) in result
    assert str(file2) in result
