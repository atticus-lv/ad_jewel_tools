import bpy
from mathutils import Vector

from ops.utils import est_curve_length
from ops.ops_utils.op_template import ADJT_OT_ModalTemplate


class ADJT_OT_OffsetCurvByLength(ADJT_OT_ModalTemplate):
    """Offset Curve Origin by its length
按长度偏移曲线原点"""
    bl_idname = 'curve.adjt_offset_curve_by_length'
    bl_label = 'Offset Curve by Length'
    bl_options = {"REGISTER", "UNDO"}

    offset_list = [
        Vector((0.5, 0, 0)),
        Vector((0, 0.5, 0)),
        Vector((-0.5, 0, 0)),
        Vector((0, -0.5, 0)),
    ]
    offset_list_index = 0

    tips = [
        '',
        'Wheel UP/DOWN to change origin direction',
        'Left Confirm, Right to cancel'
    ]

    @classmethod
    def poll(self, context):
        if context.active_object is not None and len(context.selected_objects) == 1:
            return context.active_object.mode == 'OBJECT' and context.active_object.type == 'CURVE'

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'TIMER':
            # fade drawing
            if self._cancel or self._finish:
                self.finish(context)
                if self.ui_delay > 0:
                    self.ui_delay -= 0.01
                else:
                    if self.alpha > 0:
                        self.alpha -= 0.02  # fade
                    else:
                        return self.remove_handle(context)

        if self._finish or self._cancel: return {'PASS_THROUGH'}

        if event.type == "MIDDLEMOUSE" or (
                (event.alt or event.shift or event.ctrl) and event.type == "MIDDLEMOUSE"):
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE':
            self._finish = True

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._cancel = True

        elif event.type == "WHEELUPMOUSE" and not (self._cancel or self._finish):
            self.offset_list_index -= 1
            if self.offset_list_index < 0: self.offset_list_index = 3
            context.scene.cursor.location = self.offset_list[self.offset_list_index]
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            context.scene.cursor.location = self.cur_ori_loc
            self.draw_title()

        elif event.type == "WHEELDOWNMOUSE" and not (self._cancel or self._finish):
            self.offset_list_index += 1
            if self.offset_list_index > 3: self.offset_list_index = 0
            context.scene.cursor.location = self.offset_list[self.offset_list_index]
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            context.scene.cursor.location = self.cur_ori_loc
            self.draw_title()

        return {"RUNNING_MODAL"}

    def draw_title(self):
        ori_loc = list(self.offset_list[self.offset_list_index])
        f = [round(d, 3) for d in ori_loc]
        self.title = 'Origin: ' + str(f)[1:-1]

    def finish(self, context):
        if self._cancel:
            context.scene.cursor.location = self.origin_loc
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            context.scene.cursor.location = self.cur_ori_loc

    def pre(self, context, event):
        self.curve = context.active_object
        self.curve_len = est_curve_length(self.curve)
        self.origin_loc = tuple(self.curve.location)  # use tuple to prevent overwrite

        x = self.origin_loc[0]
        y = self.origin_loc[1]

        self.offset_list = [
            Vector((0.5 * self.curve_len + x, y, 0)),
            Vector((x, 0.5 * self.curve_len + y, 0)),
            Vector((-0.5 * self.curve_len + x, y, 0)),
            Vector((x, -0.5 * self.curve_len + y, 0)),
        ]

        self.cur_ori_loc = tuple(context.scene.cursor.location)  # use tuple to prevent overwrite

    def main(self, context):
        return {"RUNNING_MODAL"}


def register():
    bpy.utils.register_class(ADJT_OT_OffsetCurvByLength)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_OffsetCurvByLength)
