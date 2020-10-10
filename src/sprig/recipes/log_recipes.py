import asyncio
import logging
import time

from sprig import logs, logs_async

logger = logging.getLogger(__name__)

class SlowHandler(logging.StreamHandler):
    def __init__(self, prefix):
        super(SlowHandler, self).__init__()
        self.setFormatter(logging.Formatter(prefix+logging.BASIC_FORMAT))
    def emit(self, record: logging.LogRecord) -> None:
        time.sleep(0.2)
        super().emit(record)

def main():
    for word in "Her name is Alice".split():
        print(word)
        logger.info("%s", word)


def t_main():
    with logs.thread_bridge(logging.root, SlowHandler("T:")):
        main()

def p_main():
    with logs.thread_bridge(logging.root, SlowHandler("P:")):
        main()

async def a_main():
    async with logs_async.bridge(logging.root, SlowHandler("A:")):
        main()

if __name__ == '__main__':
    logging.root.setLevel(level=logging.NOTSET)
    t_main()
    p_main()
    asyncio.run(a_main())
    print("Done")
