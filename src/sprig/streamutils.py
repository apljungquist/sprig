import collections
import heapq
import itertools
from typing import (
    TypeVar,
    Any,
    Callable,
    Optional,
    Dict,
    Deque,
    Tuple,
    List,
    Generic,
)

from typing_extensions import Protocol

from sprig import iterutils

_SENTINEL = object()


class ComparableT(Protocol):  # pylint: disable=too-few-public-methods
    def __lt__(self, other):
        ...


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V", bound=ComparableT)


class BucketMerger(Generic[T, U, V]):
    """Sort a partially sorted iterator

    It must be possible to bucket the iterator into individually sorted iterators.

    A typical use case for this would be sorting incoming TCP messages from several
    sources; Thanks to TCP the messages from each source are guaranteed to be ordered
    and thanks to IP the messages can be bucketed by the source.

    Notice in the example below that
    * the vowels and consonants are each sorted in the input, and
    * the output is sorted without regard for the case of the letter.

    >>> emitted = []
    >>> lower = lambda x: x.lower()
    >>> vowel = lambda x: x.lower() in "aeiou"
    >>> merger = BucketMerger(lower, vowel, emitted.append)
    >>> merger.register(False)
    >>> merger.register(True)
    >>> for c in "aEbcdifgh": merger.put(c)
    >>> merger.close()
    >>> "".join(emitted)
    'abcdEfghi'
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        sort_key: Callable[[T], V],
        bucket_key: Callable[[T], U],
        callback: Callable[[T], Any],
    ) -> None:
        self._get_time = sort_key
        self._get_src = bucket_key
        self._callback = callback

        self._channels: Dict[U, Deque[T]] = {}
        self._blocking: Dict[U, Tuple[int, U, Deque[T]]] = {}
        self._available: List[Tuple[V, int, U, Deque[T]]] = []
        self._tie_breakers = itertools.count()
        self._now: Optional[V] = None

    def register(self, src: U) -> None:
        if src in self._channels:
            raise ValueError

        items: Deque[T] = collections.deque()
        self._channels[src] = items
        self._blocking[src] = next(self._tie_breakers), src, items

    def unregister(self, src: U) -> None:
        if src not in self._channels:
            raise KeyError

        msgs = self._channels.pop(src)
        if msgs:
            msgs.append(_SENTINEL)  # type: ignore
        else:
            del self._blocking[src]
            self._flush()

    def put(self, msg: T) -> None:
        when = self._get_time(msg)
        if self._now is not None and when < self._now:
            raise ValueError

        src = self._get_src(msg)
        msgs = self._channels[src]

        if msgs:
            msgs.append(msg)
        else:
            msgs.append(msg)
            tie_breaker, _, _ = self._blocking.pop(src)
            heapq.heappush(
                self._available, (self._get_time(msg), tie_breaker, src, msgs)
            )
            self._flush()

    def _flush(self):
        while not self._blocking and self._available:
            when, tie_breaker, src, msgs = heapq.heappop(self._available)
            msg = msgs.popleft()

            self._now = when
            self._callback(msg)

            if msgs:
                if msgs[0] is not _SENTINEL:
                    heapq.heappush(
                        self._available,
                        (self._get_time(msgs[0]), tie_breaker, src, msgs),
                    )
            else:
                self._blocking[src] = tie_breaker, src, msgs

    def close(self) -> None:
        for src in list(self._channels):
            self.unregister(src)


class Bucket:
    def __init__(self):
        self._deque = collections.deque()

    def append(self, item):
        self._deque.append(item)

    def __len__(self):
        return len(self._deque)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self._deque.popleft()
        except IndexError:
            raise StopIteration


class SimpleBucketMerger:
    """A simpler and less flexible version

    Implemented as warm up, kept for comparison (for now).
    """

    def __init__(self, sort_key, bucket_key, bucket_keys, callback=None):
        self._bucket_key = bucket_key
        self._callback = callback
        self._buckets = {k: Bucket() for k in bucket_keys}
        self._sorted = iterutils.imerge(self._buckets.values(), sort_key)

    def put(self, item):
        self._buckets[self._bucket_key(item)].append(item)
        while all(self._buckets.values()):
            self._callback(next(self._sorted))

    def close(self):
        for item in self._sorted:
            self._callback(item)
