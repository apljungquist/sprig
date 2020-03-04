"""Foolproof(?) time handling

Using mostly the standard library, many questionable type hints, and a few functions to
bootstrap the whole mess.
"""
from __future__ import annotations

from typing import Any, overload

class UnixDuration:
    def __init__(self, seconds: float) -> None: ...
    def __lt__(self, other: UnixDuration) -> bool: ...
    def __le__(self, other: UnixDuration) -> bool: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ge__(self, other: UnixDuration) -> bool: ...
    def __gt__(self, other: UnixDuration) -> bool: ...
    @overload
    def __add__(self, other: UnixDuration) -> UnixDuration: ...
    @overload
    def __add__(self, other: UnixTime) -> UnixTime: ...
    def __sub__(self, other: UnixDuration) -> UnixDuration: ...

class UnixTime:
    def __init__(self, seconds: float) -> None: ...
    def __lt__(self, other: UnixTime) -> bool: ...
    def __le__(self, other: UnixTime) -> bool: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ge__(self, other: UnixTime) -> bool: ...
    def __gt__(self, other: UnixTime) -> bool: ...
    def __add__(self, other: UnixDuration) -> UnixTime: ...
    @overload
    def __sub__(self, other: UnixDuration) -> UnixTime: ...
    @overload
    def __sub__(self, other: UnixTime) -> UnixDuration: ...

class LocalDuration:
    # TODO: Define some functions and properties
    pass

class LocalTime:
    # TODO: Define some functions and properties
    # TODO: Consider removing
    def isoformat(self) -> str: ...

class TimeZone:
    pass

def timezone(str) -> TimeZone: ...
def ut_from_now() -> UnixTime: ...
def lt_from_now() -> LocalTime: ...
def ut_from_lt(lt: LocalTime, tz: TimeZone) -> UnixTime: ...
def lt_from_ut(ut: UnixTime, tz: TimeZone) -> LocalTime: ...
def strptime(date_string: str, format: str) -> LocalTime: ...
def strftime(lt: LocalTime, format: str) -> str: ...
