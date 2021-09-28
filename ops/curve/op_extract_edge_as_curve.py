import bpy
from ..utils import copy_obj
from ..ops_utils.op_template import ADJT_OT_ModalTemplate
from ..utils import draw_pre, draw_post, draw_nurbs_curve


def draw_move_object_callback_px(self, context):
    draw_pre(width=2)

    for curve in self.draw_curves:
        draw_nurbs_curve(curve, color=(1, 0, 0, self.alpha))

    draw_post()


class ADJT_OT_ExtractEdgeAsCurve(ADJT_OT_ModalTemplate):
    """Select one obj in object mode and edges in edge mode
物体模式选择一个物体，并且在编辑模式选择边"""
    bl_idname = 'curve.adjt_extract_edge_as_curve'
    bl_label = 'Extract edge as curve'
    bl_options = {"REGISTER", "UNDO"}

    tips = [
        '',
    ]

    @classmethod
    def poll(self, context):
        if context.active_object is not None and len(context.selected_objects) == 1:
            return context.active_object.mode == 'EDIT' and context.active_object.type == 'MESH'

    def append_handle(self, context):
        args = (self, context)
        self._handle_curve = bpy.types.SpaceView3D.draw_handler_add(draw_move_object_callback_px, args, 'WINDOW',
                                                                    'POST_VIEW')
        super().append_handle(context)

    def remove_handle(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle_curve, 'WINDOW')
        return super().remove_handle(context)

    def main(self, context):
        # update bmesh
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        # copy
        ori_obj = context.active_object
        ori_name = ori_obj.name
        ori_obj.name = 'Curve from ' + ori_obj.name

        new_obj = copy_obj(ori_obj)
        new_obj.name = ori_name
        for mod in ori_obj.modifiers:
            ori_obj.modifiers.remove(mod)

        self.tips.clear()
        self.tips.append('')
        self.tips.append(f'"{ori_obj.name}" has been extract')

        # print("NEW", new_obj)
        ori_obj.select_set(1)
        new_obj.select_set(0)
        # print("SEL", context.selected_objects)
        # print("ACTIVE", context.active_object)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='EDGE')

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='CURVE')

        # set nurbs type
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.spline_type_set(type='NURBS')
        bpy.ops.object.mode_set(mode='OBJECT')

        curve = context.active_object
        curve.data.splines[0].use_endpoint_u = True

        self.draw_curves.clear()
        self.draw_curves.append(curve)

        self._finish = True


def register():
    bpy.utils.register_class(ADJT_OT_ExtractEdgeAsCurve)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ExtractEdgeAsCurve)
