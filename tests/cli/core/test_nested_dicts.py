from cli.core.nested_dicts import set_dict_value


def test_set_dict_value():
    original_dict = {}
    path = "a.b.c"

    result = set_dict_value(original_dict, path, "test")

    assert result == {"a": {"b": {"c": "test"}}}


def test_set_dict_value_same_leaf():
    original_dict = {"a": {"b": {"c": "old_value"}}}
    path = "a.b.d"

    result = set_dict_value(original_dict, path, "test")

    assert result == {"a": {"b": {"c": "old_value", "d": "test"}}}
