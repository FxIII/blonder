import asyncio
import aiomas


class NS(aiomas.Agent):
    objects = {}

    @aiomas.expose
    def register(self, name, address):
        self.objects[name] = address
        return True

    @aiomas.expose
    def safeRegister(self, name, address):
        if name in self.objects:
            return False
        return self.register(name, address)

    @aiomas.expose
    def list(self):
        return list(self.objects.keys())

    @aiomas.expose
    def resolve(self, name):
        return self.objects.get(name)


async def setup():
    container = await aiomas.Container.create(('0.0.0.0', 5555), as_coro=True)
    agent = NS(container)
    agent.register(".", agent.addr)
    print(agent.addr)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(setup())
    loop.run_forever()
