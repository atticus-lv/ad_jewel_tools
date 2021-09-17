import bpy
from .utils import copy_obj
from bpy.props import BoolProperty


class ADJT_OT_FlowMeshOnCurve(bpy.types.Operator):
    """First select mesh then add select curve
先选网格物体再加选曲线曲线"""
    bl_idname = "adjt.flow_mesh_on_curve"
    bl_label = "流动网格到曲线"
    bl_options = {'REGISTER', 'UNDO'}

    use_array: BoolProperty(name='Use Array', default=False)

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'CURVE' and len(context.selected_objects) == 2

    def execute(self, context):
        ori_curve = context.active_object
        ori_mesh = [obj for obj in context.selected_objects if obj != ori_curve][0]
        self.add_modifiers(ori_mesh, ori_curve)

        return {'FINISHED'}

    def add_modifiers(self, obj, curve):
        if self.use_array:
            mod_array = obj.modifiers.new(name ='Array',type = 'ARRAY')
            mod_array.fit_type = 'FIT_CURVE'
            mod_array.curve = curve

        mod_curve = obj.modifiers.new(name ='Curve',type = 'CURVE')
        mod_curve.object = curve


def register():
    bpy.utils.register_class(ADJT_OT_FlowMeshOnCurve)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_FlowMeshOnCurve)