"""Utilities for working with intervals."""
import itertools

_LEFT = "L"
_RIGHT = "R"
assert _LEFT < _RIGHT


def _subsets(items):
    """Iterate over all possible subsets of `items`.

    The order in which subsets appear is not guaranteed.

    >>> sorted(_subsets([0]))
    [(0,)]
    >>> sorted(_subsets([0, 1]))
    [(0,), (0, 1), (1,)]

    >>> sorted(_subsets([0, 1, 2]))
    [(0,), (0, 1), (0, 1, 2), (0, 2), (1,), (1, 2), (2,)]
    """
    return itertools.chain.from_iterable(
        itertools.combinations(items, i + 1) for i in range(len(items))
    )


def _intersection(intervals):
    """Return the biggest interval that is a subset of all given intervals

    >>> _intersection([(10,60), (40, 90)])
    (40, 60)
    >>> _intersection([(10,60), (40, 90), (45, 55)])
    (45, 55)
    """
    lefts, rights = zip(*intervals)
    left = max(lefts)
    right = min(rights)
    # TODO: Consider raising on degenerate
    return left, right


def _endpoints(intervals):
    for tie_breaker, (key, (left, right)) in enumerate(intervals):
        yield left, _LEFT, tie_breaker, key
        yield right, _RIGHT, tie_breaker, key


def _intervals(endpoints):
    active = {}
    for when, side, _, key in endpoints:
        if side is _LEFT:
            active[key] = when
        else:
            yield key, (active.pop(key), when)


def _intersecting_subsets(endpoints):
    active = {}
    for when, side, tie_breaker, key in endpoints:
        if side is _RIGHT:
            del active[key]

        yield when, side, tie_breaker, frozenset([key])
        for keys in _subsets(active):
            yield when, side, tie_breaker, frozenset((key,) + keys)

        if side is _LEFT:
            active[key] = when


def intersecting_subsets(intervals):
    """All intervals formed by reducing subsets with intersection

    In no particular order.
    """
    items = intervals.items()
    input_endpoints = sorted(_endpoints(items))
    output_endpoints = _intersecting_subsets(input_endpoints)
    return dict(_intervals(output_endpoints))


def _intersecting_combinations(endpoints, k):
    active = {}
    for when, side, tie_breaker, key in endpoints:
        if side is _RIGHT:
            del active[key]

        for keys in itertools.combinations(active, k - 1):
            yield when, side, tie_breaker, frozenset((key,) + keys)

        if side is _LEFT:
            active[key] = when


def intersecting_combinations(intervals, k):
    """All intervals formed by reducing k-combinations with intersection

    In no particular order.
    """
    items = intervals.items()
    input_endpoints = sorted(_endpoints(items))
    output_endpoints = _intersecting_combinations(input_endpoints, k)
    return dict(_intervals(output_endpoints))


def _intersecting_products(factored_endpoints, num_factor):
    active = [set() for _ in range(num_factor)]
    for when, side, tie_breaker, (factor_num, key) in factored_endpoints:
        if side is _LEFT:
            active[factor_num].add(key)

        tmp = active[:]
        tmp[factor_num] = [key]
        for keys in itertools.product(*tmp):
            yield when, side, tie_breaker, keys

        if side is _RIGHT:
            active[factor_num].remove(key)


def intersecting_products(factors):
    """All intervals formed by reducing products with intersection.

    In other words every interval that can be formed by intersecting exactly one
    interval from each of the `factors`.

    >>> intersecting_products([{0: (1, 7)}, {1:(3, 9)}, {2: (0, 2), 3: (0,4)}])
    {(0, 1, 3): (3, 4)}

    Note that the time complexity worse if intervals within a factor may intersect.
    It is potentially much worse if a large portion of the intervals do intersect.

    """
    items = [
        ((factor_num, key), (left, right))
        for factor_num, factor in enumerate(factors)
        for key, (left, right) in factor.items()
    ]
    input_endpoints = sorted(_endpoints(items))
    output_endpoints = _intersecting_products(input_endpoints, len(factors))
    return dict(_intervals(output_endpoints))
