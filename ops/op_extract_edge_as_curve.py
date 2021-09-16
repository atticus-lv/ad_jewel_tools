import bpy
from .utils import copy_obj


class ADJT_OT_ExtractEdgeAsCurve(bpy.types.Operator):
    bl_idname = 'adjt.extract_edge_as_curve'
    bl_label = 'Extract Edge As Curve 边到曲线'

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            return context.active_object.mode == 'EDIT' and context.active_object.type == 'MESH'

    def execute(self, context):
        # copy
        obj = copy_obj(context.active_object)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.curve.select_all(action='DESELECT')
        obj.select_set(1)

        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='EDGE')

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='CURVE')

        return {'FINISHED'}
