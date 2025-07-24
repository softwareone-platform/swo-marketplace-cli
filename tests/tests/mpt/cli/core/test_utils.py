from cli.core.utils import get_files_path, set_dict_value


def test_set_dict_value():
    original_dict = {}
    path = "a.b.c"

    assert set_dict_value(original_dict, path, "test") == {"a": {"b": {"c": "test"}}}


def test_set_dict_value_same_leaf():
    original_dict = {"a": {"b": {"c": "old_value"}}}
    path = "a.b.d"

    assert set_dict_value(original_dict, path, "test") == {
        "a": {"b": {"c": "old_value", "d": "test"}}
    }


def test_get_files_path_no_files():
    files = get_files_path(["no_file"])

    assert files == []


def test_get_files_path_single_file(tmp_path):
    file = tmp_path / "file.xlsx"
    file.touch()

    files = get_files_path([str(file)])

    assert len(files) == 1
    assert str(file) in files


def test_get_files_path_multiple_files(tmp_path):
    file1 = tmp_path / "file1.xlsx"
    file1.touch()
    file2 = tmp_path / "file2.xlsx"
    file2.touch()

    files = get_files_path([str(file1), str(file2)])

    assert len(files) == 2
    assert str(file1) in files
    assert str(file2) in files


def test_get_files_path_directory(tmp_path):
    file1 = tmp_path / "file.xlsx"
    file1.touch()
    file2 = tmp_path / "file2.xlsx"
    file2.touch()

    files = get_files_path([str(tmp_path)])
    assert len(files) == 2
    assert str(file1) in files
    assert str(file2) in files
