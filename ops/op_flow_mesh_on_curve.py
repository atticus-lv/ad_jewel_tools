import bpy
from .utils import copy_obj
from bpy.props import BoolProperty, EnumProperty


class ADJT_OT_FlowMeshOnCurve(bpy.types.Operator):
    """First select mesh then add select curve
先选网格物体再加选曲线"""
    bl_idname = "adjt.flow_mesh_on_curve"
    bl_label = "Flow mesh on curve"
    bl_options = {'REGISTER', 'UNDO'}

    use_array: BoolProperty(name='Use Array', default=True)

    array_direction: EnumProperty(name='Array direction', items=[
        ('X', 'X', ''),
        ('Y', 'Y', ''),
        ('Z', 'Z', ''),
    ])
    tmp_array_offset = [1, 1, 1]

    ori_mesh = None
    ori_curve = None

    mod_array = None
    mod_curve = None

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'CURVE' and len(context.selected_objects) == 2

    def finish(self, context, cancel=False):
        self.remove_modifiers(remove_all=cancel)

        if self.cursor_set:
            context.window.cursor_modal_restore()

        # draw Handle
        context.window_manager.event_timer_remove(self._timer)
        # bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

        # set active object
        context.view_layer.objects.active = self.ori_curve if cancel else self.ori_mesh

        return {'FINISHED'} if cancel else {'CANCELLED'}

    def modal(self, context, event):
        if event.type == "MIDDLEMOUSE" or ((event.alt or event.shift) and event.type == "MIDDLEMOUSE"):
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE':
            return self.finish(context)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.report({'INFO'}, "Cancelled！")
            return self.finish(context, cancel=True)

        elif event.type == "A" and event.value == "PRESS":
            self.use_array = True if self.use_array == False else False
            self.mod_array.show_viewport = True if self.use_array else False

        elif event.type in {'X', 'Y', 'Z'}:
            # save to cache
            self.tmp_array_offset[0] = self.mod_array.relative_offset_displace[0]
            self.tmp_array_offset[1] = self.mod_array.relative_offset_displace[1]
            self.tmp_array_offset[2] = self.mod_array.relative_offset_displace[2]

            if event.type == 'X' and event.value == "PRESS":
                self.mod_array.relative_offset_displace[1] = 0
                self.mod_array.relative_offset_displace[2] = 0

            elif event.type == 'Y' and event.value == "PRESS":
                self.mod_array.relative_offset_displace[0] = 0
                self.mod_array.relative_offset_displace[2] = 0

            elif event.type == 'Z' and event.value == "PRESS":
                self.mod_array.relative_offset_displace[0] = 0
                self.mod_array.relative_offset_displace[1] = 0
            # set direction
            self.array_direction = event.type

        context.area.tag_redraw()
        # change values
        if event.type == 'MOUSEMOVE':
            self.mouseDX = self.mouseDX - event.mouse_x
            self.mouseDY = self.mouseDY - event.mouse_y
            multiplier = 0.001 if event.shift else 0.005
            # multi offset
            offset = self.mouseDX
            if self.array_direction == 'X':
                self.mod_array.relative_offset_displace[0] -= offset * multiplier
            elif self.array_direction == 'Y':
                self.mod_array.relative_offset_displace[1] -= offset * multiplier
            else:
                self.mod_array.relative_offset_displace[2] -= offset * multiplier

            # reset
            self.mouseDX = event.mouse_x
            self.mouseDY = event.mouse_y

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # set modifier
        self.ori_curve = context.active_object
        self.ori_mesh = [obj for obj in context.selected_objects if obj != self.ori_curve][0]
        self.mod_array, self.mod_curve = self.add_modifiers()

        # set active object as mesh for easier operate
        context.view_layer.objects.active = self.ori_mesh

        # modal
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y

        # icon
        self.cursor_set = True
        context.window.cursor_modal_set('MOVE_X')

        # append handle
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def remove_modifiers(self, remove_all=False):
        if self.use_array is False:
            self.ori_mesh.modifiers.remove(self.mod_array)
        if remove_all:
            self.ori_mesh.modifiers.remove(self.mod_array)
            self.ori_mesh.modifiers.remove(self.mod_curve)

    def add_modifiers(self):
        mod_array = self.ori_mesh.modifiers.new(name='Array', type='ARRAY')
        mod_array.fit_type = 'FIT_CURVE'
        mod_array.curve = self.ori_curve
        mod_array.use_merge_vertices = True
        mod_array.use_merge_vertices_cap = True

        mod_curve = self.ori_mesh.modifiers.new(name='Curve', type='CURVE')
        mod_curve.object = self.ori_curve
        return mod_array, mod_curve


def register():
    bpy.utils.register_class(ADJT_OT_FlowMeshOnCurve)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_FlowMeshOnCurve)
