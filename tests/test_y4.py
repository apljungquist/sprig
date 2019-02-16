import collections

from sprig import y4

import pytest

_SRC_DIRECTIVES = {
    "d",
    "dd",
    "ddd",
    "dddd",
    "f",
    "ff",
    "fff",
    "ffff",
    "fffff",
    "ffffff",
    "fffffff",
    "F",
    "FF",
    "FFF",
    "FFFF",
    "FFFFF",
    "FFFFFF",
    "FFFFFFF",
    "g",
    "h",
    "hh",
    "H",
    "HH",
    "K",
    "m",
    "mm",
    "M",
    "MM",
    "MMM",
    "MMMM",
    "s",
    "ss",
    "t",
    "tt",
    "y",
    "yy",
    "yyy",
    "yyyy",
    "yyyyy",
    "z",
    "zz",
    "zzz",
}

_DST_DIRECTIVES = {
    # C89 directives
    "%a",
    "%A",
    "%w",
    "%d",
    "%b",
    "%B",
    "%m",
    "%y",
    "%Y",
    "%H",
    "%I",
    "%p",
    "%M",
    "%S",
    "%f",
    "%z",
    "%Z",
    "%j",
    "%U",
    "%W",
    "%c",
    "%x",
    "%X",
    # ISO 8601 directives not part of C89
    "%G",
    "%u",
    "%V",
}


def test_shadowing_builtins_raises():
    with pytest.raises(ValueError):
        y4._translate("{yyyy}", yyyy='Pig')


@pytest.mark.parametrize(
    'directives', [y4._TRANSLATIONS.keys(),
                   y4._TRANSLATIONS.values()],
    ids=['src', 'dst']
)
def test_translations_are_unique(directives):
    """
    I assume each intuitive directives should behave differently. Therefore it
    is not reasonable for two of them to translate to the same C89 directive.
    """
    duplicate_directives = {
        directive
        for directive, count in collections.Counter(directives).items()
        if count > 1
    }
    assert not duplicate_directives


# I am not sure it is possible create a complete one-to-one mapping between the two
# styles of directives. As such the next two tests serve mostly to document what
# directives have not been translated
@pytest.mark.xfail(strict=True)
def test_all_source_directives_are_translated():
    actual = set(y4._TRANSLATIONS)
    expected = _SRC_DIRECTIVES
    assert actual == expected


@pytest.mark.xfail(strict=True)
def test_all_destination_directives_are_translated():
    actual = set(y4._TRANSLATIONS.values())
    expected = _DST_DIRECTIVES
    assert actual == expected
