import bpy
from bpy.props import EnumProperty
from mathutils import Vector

from .utils import est_curve_length
from .op_utils import ADJT_OT_ModalTemplate


class ADJT_OT_OffsetCurvByLength(ADJT_OT_ModalTemplate):
    """Offset Curve Origin by its length
按长度偏移曲线原点"""
    bl_idname = 'adjt.offset_curve_by_length'
    bl_label = 'Offset Curve by Length'
    bl_options = {"REGISTER", "UNDO"}

    direction = 'X'
    offset_len = 0.5

    curve = None
    curve_len = 0
    origin_loc = [0, 0, 0]
    cur_ori_loc = [0, 0, 0]

    tips = [
        '',
        'X/Y to toggle direction',
        'Left Confirm, Right to cancel'
    ]

    @classmethod
    def poll(self, context):
        if context.active_object is not None and len(context.selected_objects) == 1:
            return context.active_object.mode == 'OBJECT' and context.active_object.type == 'CURVE'

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == "MIDDLEMOUSE" or (
                (event.alt or event.shift or event.ctrl) and event.type == "MIDDLEMOUSE"):
            return {'PASS_THROUGH'}

        if event.type == 'TIMER':
            # fade drawing
            if self._cancel or self._finish:
                self.finish(context)

                if self.ui_delay > 0:
                    self.ui_delay -= 0.01
                    self.finish(context)
                else:
                    if self.alpha > 0:
                        self.alpha -= 0.02  # fade
                    else:
                        return self.remove_handle(context)

        if event.type == 'LEFTMOUSE':
            self._finish = True

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self._cancel = True

        if event.type == "X" and event.value == 'PRESS':
            self.direction = 'X'
            self.offset_len = '-0.5' if self.offset_len != '-0.5' else '0.5'
            self.offset_curve(context)
        return {"RUNNING_MODAL"}

    def finish(self, context):
        if self.origin_loc != self.curve.location:
            context.scene.cursor.location = Vector(tuple(self.origin_loc))
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            context.scene.cursor.location = self.cur_ori_loc

    def offset_curve(self, context):
        x = self.origin_loc[0]
        y = self.origin_loc[1]
        z = self.origin_loc[2]

        if self.direction == 'X':
            x += self.curve_len
        elif self.direction == 'Y':
            y += self.curve_len

        context.scene.cursor.location = Vector((x, y, z))

        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        context.scene.cursor.location = self.cur_ori_loc

    def main(self, context):
        self.curve = context.active_object
        self.curve_len = est_curve_length(self.curve) * float(self.offset_len)
        self.origin_loc = self.curve.location

        self.cur_ori_loc = context.scene.cursor.location

        return {"RUNNING_MODAL"}


def register():
    bpy.utils.register_class(ADJT_OT_OffsetCurvByLength)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_OffsetCurvByLength)
