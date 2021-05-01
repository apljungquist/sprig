import pytest

from sprig import comb


@pytest.mark.parametrize("k", [1, 2, 3, 5])
def test_comb_benchmark(k):
    comb.Combinations.clear_cache()
    cs = comb.Combinations(range(52), k)
    [cs[i] for i in range(len(cs))]
