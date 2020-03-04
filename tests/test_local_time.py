import datetime

import pytz

from sprig import local_time


def test_misc() -> None:
    tz = local_time.timezone("Europe/Stockholm")
    ut0 = local_time.ut_from_now()
    lt0 = local_time.lt_from_ut(ut0, tz)
    lt1 = local_time.lt_from_now()
    # lt = local_time.strptime("20200329_020000", "%Y%m%d_%H%M%S")
    print()
    print(lt0.isoformat())
    print(lt1.isoformat())


def test_fail() -> None:
    ut = local_time.ut_from_now()
    tz = pytz.timezone("Europe/Stockholm")
    lt = datetime.datetime.fromtimestamp(ut)  # mypy will be most unhappy, unlike me
    ud = local_time.ut_from_now() - ut
    print(ud)
    print(ud + ud)
    print(ut + ud)
    print(ut - ud)
    print(ud - ut)  # mypy should be unhappy
    print(ud + 10)  # mypy should be unhappy
    print(ud + local_time.UnixDuration(10))
    # etc
