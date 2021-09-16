import bpy
from .utils import copy_obj


class ADJT_OT_ExtractEdgeAsCurve(bpy.types.Operator):
    """Select one obj in object mode and edges in edge mode
物体模式选择一个物体，并且在编辑模式选择边"""
    bl_idname = 'adjt.extract_edge_as_curve'
    bl_label = '边到曲线'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        if context.active_object is not None and len(context.selected_objects) == 1:
            return context.active_object.mode == 'EDIT' and context.active_object.type == 'MESH'

    def execute(self, context):
        # copy
        ori_obj = context.active_object
        ori_name = ori_obj.name
        ori_obj.name = 'Curve from' + ori_obj.name
        new_obj = copy_obj(ori_obj)
        new_obj.name = ori_name

        print("NEW", new_obj)
        ori_obj.select_set(1)
        new_obj.select_set(0)
        print("SEL", context.selected_objects)
        print("ACTIVE", context.active_object)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='EDGE')

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='CURVE')

        # restore
        ori_obj = None
        new_obj = None
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ADJT_OT_ExtractEdgeAsCurve)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ExtractEdgeAsCurve)
