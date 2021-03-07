import contextlib
import itertools
import logging
import math
import time
from typing import Tuple, NamedTuple

logger = logging.getLogger(__name__)


class Outpost(NamedTuple):
    path: Tuple[str]
    distance: float


class AdjacencyMap(dict):
    @classmethod
    def new_from_edge_list(cls, edge_list):
        result = cls()
        for head, tail, weight in edge_list:
            result[head][tail] = weight
        return result

    def __missing__(self, key):
        result = {}
        self[key] = result
        return result

    def _next_frontier(self, curr_frontier):
        next_frontier = curr_frontier.copy()
        for tail, tail_outpost in curr_frontier.items():
            for head, weight in self[tail].items():
                if head in tail_outpost.path:
                    continue  # avoid cycle
                head_outpost = Outpost(tail_outpost.path + (head,), tail_outpost.distance + weight)
                if head in curr_frontier and head_outpost.distance < curr_frontier[head].distance + weight:
                    continue  # no improvement
                next_frontier[head] = head_outpost
        return next_frontier

    def longest_path(self, start, goal, max_length=None):
        curr_frontier = {start: Outpost((start,), 0)}
        for i in itertools.islice(itertools.count(), max_length):
            prev_frontier, curr_frontier = curr_frontier, self._next_frontier(curr_frontier)
            if prev_frontier == curr_frontier:
                logger.info("Search converged after %i iterations", i)
                if goal not in curr_frontier:
                    raise ValueError("Converged without finding a path")
                break
        else:
            logger.info("Search did not converge, result may be suboptimal")
            if goal not in curr_frontier:
                raise ValueError("Reached length limit without finding a path")

        return curr_frontier[goal]


def sample_edge_list():
    return [
        (head, tail, math.log(rate))
        for head, tail, rate in [
            ("a", "b", 2),  # 1 a buys 2 b
            ("b", "c", 3),
            ("c", "d", 5),
            ("c", "o", 1 / 7),
            ("c", "d", 11),
            ("d", "o", 1 / 13),
        ]
    ]


@contextlib.contextmanager
def timer():
    t0 = time.perf_counter_ns()
    yield
    t1 = time.perf_counter_ns()
    print(f"Ran in {(t1 - t0) / 1e9} seconds")


def main():
    map = AdjacencyMap.new_from_edge_list(sample_edge_list())
    with timer():
        best = map.longest_path("a", "o")

    time.sleep(0.1)  # time to flush logs
    for tail, head in zip(best.path[:-1], best.path[1:]):
        print(f"{tail} -> {head}: {math.exp(map[tail][head])}")
    print("")
    print(f"{' -> '.join(best.path)}: {math.exp(best.distance):.0%}  ")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
