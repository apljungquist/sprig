import os


def _get(name: str, default: bool) -> bool:
    return os.environ.get(f"SPRIG_{name}", default)


# Not implemented
SPEEDUP_COMB = _get("SPEEDUP_COMB", False)
# Slower than reference
SPEEDUP_DICTUTILS = _get("SPEEDUP_DICTUTILS", True)
# Slower than reference and does not work for types other than int
SPEEDUP_INTERVALS = _get("SPEEDUP_INTERVALS", False)
# Not all users have speedups installed. Nonetheless an option to keep me sane
# whle developing.
REQUIRE_SPEEDUPS = _get("REQUIRE_SPEEDUPS", False)
