def test_remove_label(parser):
    data = "[aaa={b=\"c\"}]"

    assert parser._remove_array_labels(data) == "[{b=\"c\"}]"


def test_modify_label(parser):
    data = "asd      = {dsa = 5, c=\"c = 8, 6 98 {}\"  }"

    assert parser._modify_labels(data) == "\"asd\": {\"dsa\": 5, \"c\":\"c = 8, 6 98 {}\"  }"


def test_parse(parser):
    dict = parser.parse("{a=5, c=[1, 2]}")

    assert "a" in dict and dict["a"] == 5
    assert "c" in dict and len(dict["c"]) == 2
