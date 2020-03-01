"""
Some utility functions for working with iterators.
"""
import heapq
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Tuple,
    TypeVar,
)

import more_itertools  # type: ignore

T = TypeVar("T")
U = TypeVar("U")


def imerge(
    iterables: Iterable[Iterable[T]], key: Callable[[T], Any] = lambda x: x,
) -> Iterable[T]:
    """Merge individually sorted iterables to a single sorted iterator.

    This is simlar to the merge step in merge-sort except
    * it handles an arbitrary number of iterators, and
    * eagerly consumes only one item from each iterator.

    If the laziness is not needed, it is probably better to concatenate and sort.

    **Sorted normally**

    >>> list(imerge([[1, 4], [2, 3]]))
    [1, 2, 3, 4]

    **Key changes order (Note that the sorted order of inputs is different)s**

    >>> list(imerge([[4, 1], [2, 3]], key=lambda x: (x%2, x)))
    [2, 4, 1, 3]
    """
    if not callable(key):
        raise TypeError("Key must be callable")

    heap: List[Tuple[Any, int, T, Iterator[T]]] = []
    for i, iterable in enumerate(iterables):
        iterator = iter(iterable)
        try:
            v = next(iterator)
        except StopIteration:
            continue
        k = key(v)
        heapq.heappush(heap, (k, i, v, iterator))

    while heap:
        k, i, v, iterator = heapq.heappop(heap)
        yield v
        try:
            v = next(iterator)
        except StopIteration:
            continue

        k = key(v)
        heapq.heappush(heap, (k, i, v, iterator))


def bucket_merge(
    iterable: Iterable[T],
    sort_key: Callable[[T], Any],
    bucket_key: Callable[[T], U],
    buckets: Iterable[U],
) -> Iterator[T]:
    """Sort a partially sorted iterable lazily

    If the iterable can be split into individually sorted buckets then this function
    will sort it.
    """
    buckets = set(buckets)
    iterables = more_itertools.bucket(iterable, bucket_key, lambda x: x in buckets)
    yield from imerge((iterables[bucket] for bucket in buckets), key=sort_key)
