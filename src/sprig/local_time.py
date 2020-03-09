"""Foolproof time handling

Using mostly the standard library, many questionable type hints, and a few functions to
bootstrap the whole mess.
"""
from __future__ import annotations

import datetime
import time

import pytz

"""Foolproof(?) time handling

Using mostly the standard library, many questionable type hints, and a few functions to
bootstrap the whole mess.
"""
from __future__ import annotations

from typing import Any, overload, Protocol, TypeVar


class UnixDurationT(Protocol):
    def __lt__(self, other: UDT) -> bool:
        ...

    def __le__(self, other: UDT) -> bool:
        ...

    def __eq__(self, other: Any) -> bool:
        ...

    def __ge__(self, other: UDT) -> bool:
        ...

    def __gt__(self, other: UDT) -> bool:
        ...

    @overload
    def __add__(self, other: UDT) -> UDT:
        ...

    @overload
    def __add__(self, other: UTT) -> UTT:
        ...

    def __sub__(self, other: UDT) -> UDT:
        ...


UDT = TypeVar("UDT", bound=UnixDurationT)


def UnixDuration(ut: float) -> UnixDurationT:
    return ut  # type: ignore


class UnixTimeT(Protocol):
    def __lt__(self, other: UnixTimeT) -> bool:
        ...

    def __le__(self, other: UnixTimeT) -> bool:
        ...

    def __eq__(self, other: Any) -> bool:
        ...

    def __ge__(self, other: UnixTimeT) -> bool:
        ...

    def __gt__(self, other: UnixTimeT) -> bool:
        ...

    def __add__(self, other: UnixDurationT) -> UnixTimeT:
        ...

    @overload
    def __sub__(self, other: UnixDurationT) -> UnixTimeT:
        ...

    @overload
    def __sub__(self, other: UnixTimeT) -> UnixDurationT:
        ...


UTT = TypeVar("UTT", bound=UnixTimeT)


class LocalDurationT(Protocol):
    # TODO: Define some functions and properties
    pass


class LocalTimeT(Protocol):
    # TODO: Define some functions and properties
    # TODO: Consider removing
    def isoformat(self) -> str:
        ...


class TimeZoneT(Protocol):
    pass


def timezone(name: str) -> TimeZoneT:
    return pytz.timezone(name)


def ut_from_now() -> UnixTimeT:
    return time.time()  # type: ignore


def lt_from_now() -> LocalTimeT:
    return datetime.datetime.now()


def lt_from_ut(ut: UnixTimeT, tz: TimeZoneT) -> LocalTimeT:
    lt = datetime.datetime.fromtimestamp(ut)  # type: ignore
    return tz.localize(lt).replace(tzinfo=None)  # type: ignore


def ut_from_lt(lt: LocalTimeT, tz: TimeZoneT) -> UnixTimeT:
    return tz.localize(lt).timestamp()  # type: ignore


def lt_strptime(date_string: str, format: str) -> LocalTimeT:
    return datetime.datetime.strptime(date_string, format)


def lt_strftime(lt: LocalTimeT, fmt: str) -> str:
    # lt_ = cast(datetime.datetime, lt)
    return lt.strftime(fmt)  # type: ignore
