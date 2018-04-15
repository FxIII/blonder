import blonder.looper
import bpy

NSADDR = "tcp://localhost:5555/0"
CONTAINER = ("0.0.0.0", 5557)

import asyncio
import aiomas


class Factory(aiomas.Agent):
    name = None
    container = None
    ns = None
    builders = {}

    async def setup(self, name, container, nameServer):

        self.name = name
        self.container = container
        self.ns = nameServer
        await self.register("Factory", self)
        view3D = await self.createAgent(View3D, "View3D")

    @classmethod
    def registerClass(cls, prefix):
        def decorator(targetClass):
            Factory.builders[targetClass.__name__] = (targetClass, prefix)
            return targetClass

        return decorator

    @aiomas.expose
    def lookTo(self, position, allAreas=False):
        areas = [i.spaces.active.region_3d for i in bpy.context.screen.areas if i.type == "VIEW_3D"]
        if not allAreas:
            areas = areas[:1]
        for area in areas:
            area.view_location = position

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


class View3D(aiomas.Agent):
    @aiomas.expose
    def list(self):
        areas = [i.spaces.active.region_3d for i in bpy.context.screen.areas if i.type == "VIEW_3D"]
        return list(map(id, areas))

    def byID(self, areaId):
        areas = [i.spaces.active.region_3d for i in bpy.context.screen.areas if i.type == "VIEW_3D"]
        return areas [areaId]

    @aiomas.expose
    def lookTo(self, areaID, position):
        area = self.byID(areaID)
        area.view_location = position

    @aiomas.expose
    def look(self, areaID):
        area = self.byID(areaID)
        return tuple(area.view_location)

    @aiomas.expose
    def rotateView(self, areaId, rotation):
        area = self.byID(areaId)
        area.view_rotation = rotation

    @aiomas.expose
    def viewRotation(self, areaId):
        area = self.byID(areaId)
        return tuple(area.view_rotation)


@Factory.registerClass("meshes.")
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
    ns = await container.connect(NSADDR)
    factory = Factory(container)
    await factory.setup(name, container, ns)


def startService(name):
    bpy.ops.system.looper()
    loop = asyncio.get_event_loop()
    loop.create_task(setup(name))
