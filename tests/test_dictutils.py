from sprig import dictutils

import pytest

deflated_examples = [
    {"a/i": 11, "a/j": 13, "b/i/x": "17"},  # Arbitrary tree
]


@pytest.mark.parametrize("deflated_before", deflated_examples)
def test_deflate_reverses_inflate(deflated_before):
    inflated_before = dictutils.inflate(deflated_before)
    deflated_after = dictutils.deflate(inflated_before)
    assert deflated_before == deflated_after


GOOD = [
    ({}, {}),
    ({"a": "alpha", "b": "beta"}, {"alpha": "a", "beta": "b"}),
    ({"a": 0, 0: "a"}, {"a": 0, 0: "a"}),
    ({i: str(i) for i in range(100)}, {str(i): i for i in range(100)}),
]
BAD = [
    ({"a": "x", "b": {}}, TypeError),
    ({"a": "x", "b": "x"}, ValueError),
]


@pytest.mark.parametrize("example", [vs[0] for vs in GOOD + BAD])
def test_invert_does_not_mutate_imput(example):
    expected = example.copy()
    try:
        dictutils.invert(example)
    except Exception:
        pass
    assert example == expected


@pytest.mark.parametrize("example, expected", GOOD)
def test_returns_expected(example, expected):
    actual = dictutils.invert(example)
    assert actual == expected


@pytest.mark.parametrize("before, cls", BAD)
def test_raises_expected(before, cls):
    with pytest.raises(cls):
        print(dictutils.invert(before))
