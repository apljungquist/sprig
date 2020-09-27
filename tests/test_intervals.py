from random import Random

import pytest

from sprig import intervals, intervals_naive


def _rng(seed):
    if isinstance(seed, Random):
        return seed
    else:
        return Random(seed)


def _rand_intervals(seed, num_interval, min_pitch):
    rng = _rng(seed)
    result = {}
    if num_interval is None:
        num_interval = rng.randrange(1, 10)
    if min_pitch is None:
        min_pitch = 0.5

    left = 0.0
    for i in range(num_interval):
        left += min_pitch + rng.random()
        right = left + rng.random()
        result[i] = (left, right)
    return result


def _rand_factors(seed, num_factor=None, num_interval=None, min_pitch=None):
    rng = _rng(seed)
    if num_factor is None:
        num_factor = rng.randrange(2, 5)
    return [_rand_intervals(rng, num_interval, min_pitch) for i in range(num_factor)]


@pytest.mark.parametrize(
    "example", [({0: (1, 7), 1: (3, 9)}, {(0,): (1, 7), (0, 1): (3, 7), (1,): (3, 9)}),]
)
def test_intersecting_subsets_by_example(example):
    args = example[:-1]
    expected = {frozenset(k): v for k, v in example[-1].items()}
    assert intervals.intersecting_subsets(*args) == expected


@pytest.mark.parametrize(
    "example",
    [
        (
            {0: (1, 7), 1: (3, 9), 2: (4, 6)},
            2,
            {(0, 2): (4, 6), (1, 2): (4, 6), (0, 1): (3, 7)},
        ),
    ],
)
def test_intersecting_combinations_by_example(example):
    args = example[:-1]
    expected = {frozenset(k): v for k, v in example[-1].items()}
    assert intervals.intersecting_combinations(*args) == expected


# TODO: Define behavior in edge cases such as
#  * when no factors are given or
#  * at least one factor is zero length.
@pytest.mark.parametrize(
    "example",
    [
        ([{0: (1, 7)}, {1: (3, 9)}, {2: (0, 2), 3: (0, 4)}], {(0, 1, 3): (3, 4)}),
        ([{0: (1, 7)}, {1: (3, 9)}], {(0, 1): (3, 7)}),
        ([{0: (1, 7)}], {(0,): (1, 7)}),
        # works not only with numbers
        (
            [{"a": ([1, 2], [3, 4])}, {"b": ([2, 3], [4, 5])}],
            {("a", "b"): ([2, 3], [3, 4])},
        ),
    ],
)
def test_intersecting_products_by_example(example):
    args = example[:-1]
    expected = example[-1]

    assert intervals.intersecting_products(*args) == expected


@pytest.mark.parametrize("factors", [_rand_factors(i) for i in range(10)])
def test_intersecting_products_equivalent_to_naive(factors):
    actual = intervals.intersecting_products(factors)
    expected = intervals_naive.intersecting_products_naive(factors)
    assert actual == expected
