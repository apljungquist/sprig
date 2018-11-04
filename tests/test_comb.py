import functools
import itertools

import pytest
from sprig import comb

parameters = [
    ([], 0),  # 0-combinations, empty collection
    ([], 1),  # n+1 combinations, emtpy collection
    ([0], 0),  # 0-combinations, small collection
    ([0], 1),  # n-combinations, small collection
    ([0], 2),  # n+1 combinations, small collection
    ([0, 1, 2, 3, 4, 5], 0),  # 0-combinations
    ([0, 1, 2, 3, 4, 5], 1),  # 1-combinations
    ([0, 1, 2, 3, 4, 5], 3),  # k-combinations
    ([0, 1, 2, 3, 4, 4], 3),  # k-combinations, duplicate values
    ([0, 1, 2, 3, 4, 5], 5),  # n-1-combinations
    ([0, 1, 2, 3, 4, 5], 6),  # n-combinations
    ([0, 1, 2, 3, 4, 5], 7),  # n+1-combinations
]


def assert_equivalent_behaviour(func_a, func_b):
    try:
        result_a = func_a()
        exception_a = None
    except Exception as e:
        result_a = None
        exception_a = e

    try:
        result_b = func_b()
        exception_b = None
    except Exception as e:
        result_b = None
        exception_b = e

    assert type(exception_a) == type(exception_b)
    assert result_a == result_b


@pytest.mark.parametrize('s, k', parameters)
def test_correct_length(s, k):
    actual = comb.Combinations(s, k)
    expected = list(itertools.combinations(s, k))
    assert len(actual) == len(expected)


@pytest.mark.parametrize('s, k', parameters)
def test_agrees_with_itertools(s, k):
    actual = comb.Combinations(s, k)
    expected = list(itertools.combinations(s, k))
    for i in range(-2 * len(expected), 2 * len(expected)):
        print(i)
        assert_equivalent_behaviour(
            functools.partial(actual.__getitem__, i),
            functools.partial(expected.__getitem__, i),
        )
