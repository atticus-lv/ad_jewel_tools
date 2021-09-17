import bpy
from bpy.props import EnumProperty
from mathutils import Vector

from .utils import est_curve_length


class ADJT_OT_OffsetCurvByLength(bpy.types.Operator):
    """Offset Curve Origin by its length
按长度偏移曲线原点"""
    bl_idname = 'adjt.offset_curve_by_length'
    bl_label = '按长度偏移曲线'
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(name='Direction', items=[
        ('X', 'X', ''),
        ('Y', 'Y', ''),
    ])

    offset_len:EnumProperty(name='Length', items=[
        ('-0.5', '-1/2', ''),
        ('0.5', '1/2', ''),
    ])

    @classmethod
    def poll(self, context):
        if context.active_object is not None and len(context.selected_objects) == 1:
            return context.active_object.mode == 'OBJECT' and context.active_object.type == 'CURVE'

    def execute(self, context):
        curve = context.active_object
        curve_len = est_curve_length(curve) * float(self.offset_len)
        origin_loc = curve.location

        cur_ori_loc = bpy.context.scene.cursor.location  # returns a vector

        x = origin_loc[0]
        y = origin_loc[1]
        z = origin_loc[2]

        if self.direction == 'X':
            x += curve_len
        elif self.direction == 'Y':
            y += curve_len

        bpy.context.scene.cursor.location = Vector((x, y, z))

        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = cur_ori_loc

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ADJT_OT_OffsetCurvByLength)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_OffsetCurvByLength)
