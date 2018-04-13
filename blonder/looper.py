import bpy
import asyncio

_loop = asyncio.get_event_loop()
_loop._run_forever = _loop.run_forever
_loop._run_until_complete = _loop.run_until_complete


def run_once(*a, **k):
    _loop.call_soon(_loop.stop)
    _loop._run_forever()


_loop.run_forever = run_once
_loop.run_until_complete = _loop.create_task


class LooperOperator(bpy.types.Operator):
    """setup an aside event loop (somehow)"""
    bl_idname = "system.looper"
    bl_label = "Looper"

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            loop = asyncio.get_event_loop()
            loop.operator = self
            loop.run_forever()
            # change theme color, silly!
            color = context.user_preferences.themes[0].view_3d.space.gradients.high_gradient
            color.s = 1.0
            color.h += 0.01

        return {'PASS_THROUGH'}

    def execute(self, context):
        self.report({'INFO'}, 'Printing report to Info window.')
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context=None):
        if context is None:
            context = bpy.context
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():
    try:
        bpy.utils.register_class(LooperOperator)
    except:
        pass


def unregister():
    bpy.utils.unregister_class(LooperOperator)


register()
