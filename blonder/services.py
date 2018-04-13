import looper
import bpy

bpy.ops.object.looper()
NSADDR = "tcp://localhost:5555/0"
CONTAINER = ("0.0.0.0", 5557)

import asyncio
import aiomas


class Factory(aiomas.Agent):
    name = None
    container = None
    ns = None
    builders = {}

    @classmethod
    def register(cls, prefix):
        def decorator(targetClass):
            Factory.builders[targetClass.__name__] = (targetClass, prefix)
            return targetClass

        return decorator

    @aiomas.expose
    async def makeMesh(self, name):
        mesh = await self.createAgent(Mesh, "meshes." + name)
        mesh.setup(name)
        return mesh.addr

    @aiomas.expose
    async def make(self, className, name):
        targetClass, prefix = self.builders[className]
        obj = await self.createAgent(targetClass, prefix + name)
        obj.setup(name)
        return obj.addr

    async def register(self, name, obj):
        name = self.name + "." + name
        await self.ns.register(name, obj.addr)

    async def createAgent(self, cls, name):
        agent = cls(self.container)
        agent.name = name
        await self.register(name, agent)
        return agent


@Factory.register("meshes.")
class Mesh(aiomas.Agent):
    name = None
    obj = None

    def setup(self, name):
        me = bpy.data.meshes.new(name)
        self.obj = bpy.data.objects.new(name, me)
        scn = bpy.context.scene
        scn.objects.link(self.obj)
        scn.objects.active = self.obj
        self.obj.select = True

    @aiomas.expose
    def loadData(self, vertices, edges, polygons):
        self.obj.data.from_pydata(vertices, edges, polygons)


async def setup(name):
    container = await aiomas.Container.create(CONTAINER, as_coro=True)
    factory = Factory(container)
    factory.name = name
    factory.container = container
    ns = await container.connect(NSADDR)
    factory.ns = ns
    await factory.register("Factory", factory)


def startService(name):
    loop = asyncio.get_event_loop()
    loop.create_task(setup(name))
