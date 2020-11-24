import collections
import functools
import itertools
from random import Random

import pytest

from sprig import iterutils, streamutils


def _conjure_msg(label, random, timestamp):
    return label, int(timestamp)


def _conjure_mminf(
    get_one, time_between_arrival: float, num, random: Random,
):
    now = 0
    for _ in itertools.islice(itertools.count(), num):
        now += random.expovariate(1 / time_between_arrival)
        yield get_one(random, now)


def _random_interleave(iterables, random):
    iterables = [iter(it) for it in iterables]
    while iterables:
        it = random.choice(iterables)
        try:
            yield next(it)
        except StopIteration:
            iterables.remove(it)


def test_unregistering_source_unblocks():
    emitted = []
    merger = streamutils.BucketMerger(lambda x: x[1], lambda x: x[0], emitted.append)
    merger.register("a")
    merger.register("b")
    merger.put("a0")
    assert not emitted
    merger.unregister("b")
    assert emitted == ["a0"]


def test_putting_greater_unblocks_all_previous():
    emitted = []
    merger = streamutils.BucketMerger(lambda x: x[1], lambda x: x[0], emitted.append)
    merger.register("a")
    merger.register("b")
    merger.put("a0")
    merger.put("a1")
    assert not emitted
    merger.put("b2")
    assert emitted == ["a0", "a1"]


# Theoretically possible to implement but likely not worth the extra code complexity.
@pytest.mark.xfail(strict=True)
def test_putting_equal_unblocks_all():
    emitted = []
    merger = streamutils.BucketMerger(lambda x: x[1], lambda x: x[0], emitted.append)
    merger.register("a")
    merger.register("b")
    merger.put("a0")
    assert not emitted
    merger.put("b0")
    assert set(emitted) == {"a0", "b0"}


# Possible using the decorate-undecorate pattern but likely not worth the extra code
# complexity and runtime.
@pytest.mark.xfail(strict=True)
def test_sorting_stable():
    emitted = []
    merger = streamutils.BucketMerger(lambda x: x[1], lambda x: x[0], emitted.append)
    merger.register("a")
    merger.register("b")
    merger.put("a0")
    merger.put("b1")
    merger.put("a1")
    merger.close()
    assert emitted == ["a0", "b1", "a1"]


def test_sorting_stable_within_bucket():
    emitted = []
    merger = streamutils.BucketMerger(lambda x: x[1], lambda x: x[0], emitted.append)
    merger.register("a")
    merger.put("a0c")
    merger.put("a0a")
    merger.put("a0b")
    merger.close()
    assert emitted == ["a0c", "a0a", "a0b"]


@pytest.mark.parametrize("max_event", [1, 10, 100])
@pytest.mark.parametrize("num_src", [1, 10, 100])
def test_workflow_and_result_by_fuzzing(num_src, max_event):
    random = Random(max_event)
    srcs = list(range(num_src))
    msgs = list(
        _random_interleave(
            (
                _conjure_mminf(
                    functools.partial(_conjure_msg, src),
                    random.uniform(1, 10),
                    random.randint(0, max_event),
                    random,
                )
                for src in srcs
            ),
            random,
        )
    )

    def get_time(msg):
        return msg[1]

    def get_src(msg):
        return msg[0]

    expected = []
    actual = []
    merger = streamutils.BucketMerger(get_time, get_src, actual.append)
    registered_srcs = set()

    for src, when in msgs:
        if src not in registered_srcs:
            registered_srcs.add(src)
            merger.register(src)

        if actual and when < get_time(actual[-1]):
            with pytest.raises(ValueError):
                merger.put((src, when))
        else:
            merger.put((src, when))
            expected.append((src, when))

        if registered_srcs and random.random() < 0.1:
            src = random.choice(list(registered_srcs))
            registered_srcs.remove(src)
            merger.unregister(src)

    merger.close()

    # Note that bucket merge is not a stable sort
    assert actual == sorted(actual, key=get_time)
    assert collections.Counter(actual) == collections.Counter(expected)


def _eager_bucket_merger_adaptor(iterable, sort_key, bucket_key, buckets):
    result = []
    merger = streamutils.BucketMerger(sort_key, bucket_key, result.append)
    for bucket in buckets:
        merger.register(bucket)
    for item in iterable:
        merger.put(item)
    merger.close()
    return result


def _eager_simple_bucket_merger_adaptor(iterable, sort_key, bucket_key, buckets):
    result = []
    merger = streamutils.SimpleBucketMerger(
        sort_key, bucket_key, buckets, result.append
    )
    for item in iterable:
        merger.put(item)
    merger.close()
    return result


def _eager_bucket_merge_adaptor(iterable, sort_key, bucket_key, buckets):
    return list(iterutils.bucket_merge(iterable, sort_key, bucket_key, buckets))


@pytest.mark.parametrize(
    "eager_bucket_merge",
    [
        _eager_bucket_merge_adaptor,
        _eager_bucket_merger_adaptor,
        _eager_simple_bucket_merger_adaptor,
    ],
)
@pytest.mark.parametrize(
    "msgs",
    [
        # Edge cases w.r.t. length
        [],
        ["a1"],
        # Sort handles out of order items
        ["a1", "b3", "a2"],
        ["a1", "a3", "b2"],
        # Sort is not stable
        ["a2", "b2", "c2", "d2"],
    ],
)
def test_result_is_sorted_by_example(eager_bucket_merge, msgs):
    def get_src(msg):
        return msg[0]

    def get_time(msg):
        return msg[1]

    srcs = set(get_src(msg) for msg in msgs)

    actual = eager_bucket_merge(msgs, get_time, get_src, srcs)
    assert actual == sorted(actual, key=get_time)
    assert collections.Counter(actual) == collections.Counter(msgs)


@pytest.mark.parametrize(
    "eager_bucket_merge",
    [
        _eager_bucket_merge_adaptor,
        _eager_bucket_merger_adaptor,
        _eager_simple_bucket_merger_adaptor,
    ],
)
@pytest.mark.parametrize("max_event", [1, 10, 100])
@pytest.mark.parametrize("num_src", [1, 10, 100])
def test_result_is_sorted_by_fuzzing(eager_bucket_merge, num_src, max_event):
    random = Random(max_event)
    srcs = list(range(num_src))
    msgs = list(
        _random_interleave(
            (
                _conjure_mminf(
                    functools.partial(_conjure_msg, src),
                    random.uniform(1, 10),
                    random.randint(0, max_event),
                    random,
                )
                for src in srcs
            ),
            random,
        )
    )

    def get_time(msg):
        return msg[1]

    def get_src(msg):
        return msg[0]

    actual = eager_bucket_merge(msgs, get_time, get_src, srcs)
    assert actual == sorted(actual, key=get_time)
    assert collections.Counter(actual) == collections.Counter(msgs)


def test_timeout_merger_by_example():
    actual_msgs = []
    merger = streamutils.TimeoutMerger(actual_msgs.append, 10)

    def put(msg):
        actual_msgs.clear()
        merger.put(msg, msg[0], int(msg[1:]))
        return actual_msgs, merger.senders

    assert put("a10") == (["a10"], {"a"})
    assert put("b09") == ([], {"a", "b"})  # Dropped silently because new sender
    assert put("b11") == ([], {"a", "b"})
    assert put("c12") == ([], {"a", "b", "c"})
    assert put("c21") == (["b11"], {"b", "c"})
    assert put("b22") == (["c12", "c21"], {"b", "c"})  # a presumed disconnected

    with pytest.raises(ValueError):
        put("b21")  # Dropped loudly because old sender
    assert actual_msgs == []
    assert merger.senders == {"b", "c"}
