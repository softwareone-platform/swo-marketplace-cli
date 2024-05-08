from swo.mpt.cli.core.utils import set_dict_value


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
