import platform
import sys


def _get_msg():
    name = sys.implementation.name
    major = sys.implementation.version.major
    minor = sys.implementation.version.minor
    micro = sys.implementation.version.micro
    hit_msg = '{name}{minor}.{major}.{micro}... Check'.format_map(locals())
    miss_msg = '{name}{minor}.{major}.{micro}... Huh?'.format_map(locals())

    if name == 'pypy':
        if major == 3 and minor == 5:
            return hit_msg

    if name == 'cpython':
        if major == 3:
            if minor == 5:
                return hit_msg
            if minor == 6:
                return hit_msg
            if minor == 7:
                return hit_msg

    return miss_msg


def test_version_coverage():
    print(_get_msg())
