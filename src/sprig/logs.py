import contextlib
import logging
import multiprocessing as mp
import queue
import threading
from typing import Protocol, TypeVar, Optional

_T = TypeVar("_T")


class NonBlockingQueueT(Protocol):
    def put_nowait(self, item: _T) -> None:
        ...

    def get_nowait(self) -> _T:
        pass


class QueueT(NonBlockingQueueT, Protocol):
    def put(self, item: _T, block: bool = ..., timeout: Optional[float] = ...) -> None:
        ...

    def get(self, block: bool = ..., timeout: Optional[float] = ...) -> _T:
        ...


class BridgeConsumer:
    def __init__(self, cls, q: QueueT, handler: logging.Handler):
        self.q = q
        self._w = cls(target=self.run, args=(q, handler))

    @staticmethod
    def run(q: queue.Queue, handler):
        while True:
            obj = q.get()
            if obj is None:
                break
            handler.handle(obj)

    def start(self):
        self._w.start()

    def stop(self):
        self.q.put_nowait(None)

    def close(self):
        self.q.put(None)
        self._w.join()


class BridgeProducer(logging.Handler):
    def __init__(self, q: NonBlockingQueueT):
        super().__init__()
        self._q = q
        self._num_failure = 0

    def emit(self, record: logging.LogRecord) -> None:
        self._q.put_nowait(record)


@contextlib.contextmanager
def bridge(logger, p, c):
    logger.addHandler(p)
    try:
        c.start()
        with contextlib.closing(c):
            yield
    finally:
        logger.removeHandler(p)


def thread_bridge(logger, handler):
    q = queue.Queue()
    p = BridgeProducer(q)
    c = BridgeConsumer(threading.Thread, q, handler)
    return bridge(logger, p, c)


def process_bridge(logger, handler):
    q = mp.Queue()
    p = BridgeProducer(q)
    c = BridgeConsumer(mp.Process, q, handler)
    return bridge(logger, p, c)
