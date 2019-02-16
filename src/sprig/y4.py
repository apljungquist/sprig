# pylint: disable=C0301
"""
Convert datetime objects to a formatted representation using intuitive directives.

Note that only a subset of the intuitive_ and the python_ directives are implemented.

.. _intuitive: https://docs.microsoft.com/en-us/dotnet/standard/base-types/custom-date-and-time-format-strings
.. _python: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
"""
import datetime
from typing import Union

_TRANSLATIONS = {
    "yyyy": "%Y",
    "yy": "%y",
    "MMMM": "%B",
    "MMM": "%b",
    "MM": "%m",
    "dddd": "%A",
    "ddd": "%a",
    "dd": "%d",
    "HH": "%H",
    "hh": "%I",
    "mm": "%M",
    "ss": "%S",
    "tt": "%p",
    "zzz": "%z",
}


def _translate(fmt: str, *args: str, **kwargs: str) -> str:
    collisions = set(kwargs) & set(_TRANSLATIONS)
    if collisions:
        raise ValueError(
            "Shadowing build in directives: '{}'".format(collisions)
        )
    escaped_fmt = fmt.replace("%", "%%")
    return escaped_fmt.format(*args, **dict(_TRANSLATIONS, **kwargs))


def format_time(
        fmt: str,
        date_time: Union[datetime.date, datetime.time, datetime.datetime],
        *args: str, **kwargs: str
) -> str:
    """Return a string representing the date and time `date_time`.

    The result will be formatted according to `fmt`,
    using substitutions from `args` and `kwargs`.

    >>> dt = datetime.datetime(2019, 2, 15, 22, 20)
    >>> fmt = "Hello {name}! Today is {dddd} {MMMM} {dd}, {yyyy}"
    >>> format_time(fmt, dt, name='Brian')
    'Hello Brian! Today is Friday February 15, 2019'
    """
    return date_time.strftime(_translate(fmt, *args, **kwargs))


def parse_time(
        fmt: str, date_string: str, *args: str, **kwargs: str
) -> datetime.datetime:
    """Return a datetime corresponding to `date_string`.

    The `date_string` is parsed according to `fmt`,
    using substitutions from `args` and `kwargs`.

    >>> fmt = "Hello {name}! Today is {dddd} {MMMM} {dd}, {yyyy}"
    >>> date_string = "Hello Brian! Today is Friday February 15, 2019"
    >>> parse_time(fmt, date_string, name="Brian")
    datetime.datetime(2019, 2, 15, 0, 0)
    """
    return datetime.datetime.strptime(
        date_string, _translate(fmt, *args, **kwargs)
    )
