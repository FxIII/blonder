import asyncio
import threading
import time

import aiomas

NSADDR = "tcp://localhost:5555/0"

CONTAINER = ("0.0.0.0", 5556)


class AWrapper:
    def __init__(self, what):
        self._target = what
        if isinstance(what, asyncio.Future):
            self._target = self.wait(what)

    @staticmethod
    def wait(future, timeout=100):

        async def checkWait():
            startT = time.time()
            await asyncio.sleep(0.01)
            while future._state == "PENDING" and startT + timeout > time.time():
                await asyncio.sleep(1)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(checkWait())
        return future.result()

    def __getattr__(self, item):
        what = getattr(self._target, item)

        def askToDo(*a, **k):
            fret = asyncio.Future()

            async def asyncDo(*a, **k):
                try:
                    ret = await what(*a, **k)
                except Exception as e:
                    fret.set_exception(e)
                    return
                try:
                    post = self.__getattribute__("post_%s" % item)
                except AttributeError as e:
                    post = None
                if post is not None:
                    try:
                        ret = await post(ret, *a, **k)
                    except Exception as e:
                        fret.set_exception(e)
                        return
                fret.set_result(ret)

            Helper.loop.call_soon_threadsafe(asyncio.ensure_future, asyncDo(*a, **k))
            return fret

        return askToDo


class NSWrapper(AWrapper):
    @staticmethod
    async def post_resolve(target, *a, **k):
        return await Helper.container.connect(target)

    def connect(self, addr):
        fret = asyncio.Future()

        async def connect():
            try:
                ret = await Helper.container.connect(addr)
            except Exception as  e:
                fret.set_exception(e)
                return
            fret.set_result(ret)

        Helper.loop.call_soon_threadsafe(asyncio.ensure_future, connect())
        return fret


class Helper:
    loop = None
    container = None
    wrap = AWrapper

    @classmethod
    def main(cls):
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
        cls.loop.create_task(cls.setup())
        cls.loop.run_forever()

    @classmethod
    async def setup(cls):
        cls.container = await aiomas.Container.create(CONTAINER, as_coro=True)
        cls.ans = await cls.container.connect(NSADDR)
        cls.ns = NSWrapper(cls.ans)

    @classmethod
    def run(cls):
        cls.t = threading.Thread(target=cls.main)
        cls.t.start()


if __name__ == '__main__':
    Helper.main()
