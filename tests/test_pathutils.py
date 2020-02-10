import filecmp
import pathlib
from typing import Dict, Any

import pytest

from sprig import pathutils


class Link(str):
    pass


class File(str):
    pass


def create_tree(path: pathlib.Path, spec: Dict[str, Any]) -> None:
    if isinstance(spec, dict):
        path.mkdir()
        for name in spec:
            create_tree(path / name, spec[name])
    elif isinstance(spec, File):
        path.write_text(spec)
    elif isinstance(spec, Link):
        path.symlink_to(spec)
    else:
        raise ValueError


AARON = File("a teacher or lofty, bright, shining")
ABADDON = File("a destroyer")

HARD_SPEC_REFERENCE = {
    "Aaron": AARON,
    "Abaddon": ABADDON,
    "Abi": {
        "uncle_aaron": AARON,
    },
}
HARD_SPEC_INSERTION = {
    "Aaron": AARON,
    "Abaddon": ABADDON,
    "Abi": {
        "uncle_aaron": AARON,
    },
    "Baal": File("owner or lord, also husband"),
}
HARD_SPEC_DELETION = {
    "Aaron": AARON,
    "Abi": {
        "uncle_aaron": AARON,
    }
}
HARD_SPEC_SUBSTITUTED_CONTENT = {
    "Aaron": AARON,
    "Abaddon": ABADDON,
    "Abi": {
        "uncle_aaron": ABADDON,
    },
}
HARD_SPEC_SUBSTITUTED_MODE = {
    "Aaron": AARON,
    "Abaddon": ABADDON,
    "Abi": {
        "uncle_aaron": {},
    },
}
SOFT_SPEC_REFERENCE = {
    "Aaron": AARON,
    "Abaddon": ABADDON,
    "Abi": {
        "uncle_aaron": Link("../Aaron"),
    },
}
SOFT_SPEC_SUBSTITUTION = {
    "Aaron": AARON,
    "Abaddon": ABADDON,
    "Abi": {
        "uncle_aaron": Link("../Abaddon"),
    },
}
SOFT_SPEC_BROKEN = {
    "Aaron": AARON,
    "Abaddon": ABADDON,
    "Abi": {
        "uncle_aaron": Link("../Baal"),
    },
}


def test_rcmp_ldircmp_fails_on_links(tmp_path):
    left = tmp_path / "left"
    create_tree(left, HARD_SPEC_REFERENCE)
    right = tmp_path / "right"
    create_tree(right, SOFT_SPEC_REFERENCE)

    assert not pathutils.rcmp(pathutils.ldircmp(left, right))


def test_rcmp_dircmp_succeeds_on_links(tmp_path):
    left = tmp_path / "left"
    create_tree(left, HARD_SPEC_REFERENCE)
    right = tmp_path / "right"
    create_tree(right, SOFT_SPEC_REFERENCE)

    assert pathutils.rcmp(filecmp.dircmp(left, right))


@pytest.mark.parametrize(
    "left_spec", [HARD_SPEC_REFERENCE, SOFT_SPEC_REFERENCE]
)
@pytest.mark.parametrize(
    "right_spec",
    [
        HARD_SPEC_DELETION,
        HARD_SPEC_INSERTION,
        HARD_SPEC_SUBSTITUTED_CONTENT,
        HARD_SPEC_SUBSTITUTED_MODE,
        SOFT_SPEC_SUBSTITUTION,
        SOFT_SPEC_BROKEN,
    ],
)
@pytest.mark.parametrize("dircmp", [filecmp.dircmp, pathutils.ldircmp])
def test_rcmp_fails_on_different(tmp_path, dircmp, left_spec, right_spec):
    left = tmp_path / "left"
    create_tree(left, left_spec)
    right = tmp_path / "right"
    create_tree(right, right_spec)

    assert not pathutils.rcmp(dircmp(left, right))


@pytest.mark.parametrize("dircmp", [filecmp.dircmp, pathutils.ldircmp])
def test_rcmp_succeeds_on_identical(tmp_path, dircmp):
    left = tmp_path / "left"
    create_tree(left, HARD_SPEC_REFERENCE)
    right = tmp_path / "right"
    create_tree(right, HARD_SPEC_REFERENCE)

    assert pathutils.rcmp(dircmp(left, right))
