import asyncio
import threading
import munch

import aiomas

NSADDR = "tcp://localhost:5555/0"

CONTAINER = ("0.0.0.0", 5556)


class AWrapper:
    def __init__(self, what):
        self._target = what
        self.post = munch.Munch()

    @staticmethod
    def wait(future, timeout=100):
        import time
        async def checkWait():
            startT = time.time()
            await asyncio.sleep(0.01)
            while future._state == "PENDING" and startT + timeout > time.time():
                await asyncio.sleep(1)

        l = asyncio.get_event_loop()
        l.run_until_complete(checkWait())
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
                post = getattr(self.post, item, None)
                if post is not None:
                    try:
                        ret = await post(ret, *a, **k)
                    except Exception as e:
                        fret.set_exception(e)
                        return
                fret.set_result(ret)

            Main.loop.call_soon_threadsafe(asyncio.ensure_future, asyncDo(*a, **k))

            return fret

        return askToDo


class Main:
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
        cls.ns = AWrapper(cls.ans)
        cls.ns.post.resolve = cls.connectTo

    @classmethod
    async def connectTo(cls, target, *a, **k):
        return await cls.container.connect(target)

    @classmethod
    def run(cls):
        cls.t = threading.Thread(target=cls.main)
        cls.t.start()


if __name__ == '__main__':
    Main.main()


def test():
    ns = Main.ns
    cosimo = AWrapper(ns.wait(ns.resolve("Cosimo.Factory")))
    cosimo.wait(cosimo.makeMesh("ciccio"))
    ciccio = AWrapper(ns.wait(ns.resolve("Cosimo.meshes.ciccio")))
    coord1 = (-1.0, 1.0, 0.0)
    coord2 = (-1.0, -1.0, 0.0)
    coord3 = (1.0, -1.0, 0.0)
    coord4 = (1.0, 1.0, 0.0)

    Verts = [coord1, coord2, coord3, coord4]
    Edges = [[0, 1], [1, 2], [2, 3], [3, 0]]
    ciccio.wait(ciccio.loadData(Verts, Edges, []))


"""
import looper
import bpy
bpy.ops.object.looper()


import asyncio
import aiomas


class Callee(aiomas.Agent):
    @aiomas.expose
    def spam(self, times):
        return 'spam' * times


loop = asyncio.get_event_loop()


async def setup():
    container = await aiomas.Container.create(('localhost', 5555), as_coro=True)
    agent = Callee(container)
    print(agent.addr)


loop.create_task(setup())
"""
