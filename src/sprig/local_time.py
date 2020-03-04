"""Foolproof time handling

Using mostly the standard library, many questionable type hints, and a few functions to
bootstrap the whole mess.
"""
from __future__ import annotations

import datetime
import time

import pytz


def UnixDuration(ud):
    return ud


class UnixTime:
    pass


class LocalTime:
    pass


class TimeZone:
    pass


timezone = pytz.timezone

ut_from_now = time.time

lt_from_now = datetime.datetime.now


def lt_from_ut(ut, tz):
    lt = datetime.datetime.fromtimestamp(ut)
    return tz.localize(lt).replace(tzinfo=None)


def ut_from_lt(lt, tz):
    return tz.localize(lt).timestamp()


def lt_strptime(date_string, format):
    return datetime.datetime.strptime(date_string, format)


def lt_strftime(lt, fmt):
    # lt_ = cast(datetime.datetime, lt)
    return lt.strftime(fmt)
