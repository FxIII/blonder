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

    @aiomas.expose
    async def makeMesh(self, name):
        mesh = await self.createAgent(Mesh, "meshes." + name)
        me = bpy.data.meshes.new(name)
        mesh.obj = bpy.data.objects.new(name, me)
        scn = bpy.context.scene
        scn.objects.link(mesh.obj)
        scn.objects.active = mesh.obj
        mesh.obj.select = True
        return mesh.addr

    async def register(self, name, obj):
        name = self.name + "." + name
        await self.ns.register(name, obj.addr)

    async def createAgent(self, cls, name):
        agent = cls(self.container)
        agent.name = name
        await self.register(name, agent)
        return agent


class Mesh(aiomas.Agent):
    name = None
    obj = None

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