import asyncio
import contextlib

from sprig import logs


async def _run(q: asyncio.Queue, handler):
    while True:
        obj = await q.get()
        if obj is None:
            break
        await handler.handle(obj)

class HandlerAdapter:
    def __init__(self, adaptee):
        self._adaptee = adaptee

    async def handle(self, record):
        self._adaptee.handle(record)


@contextlib.asynccontextmanager
async def bridge(logger, handler):
    q = asyncio.Queue()
    p = logs.BridgeProducer(q)
    logger.addHandler(p)

    if asyncio.iscoroutinefunction(handler.handle):
        target = handler
    else:
        target = HandlerAdapter(handler)

    task = asyncio.get_running_loop().create_task(_run(q, target))
    try:
        yield
    finally:
        await q.put(None)
        await task
