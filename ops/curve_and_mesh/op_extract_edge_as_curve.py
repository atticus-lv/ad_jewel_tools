import bpy
from ...ops.utils import copy_obj
from ...ops.ops_utils.Template import ADJT_OT_ModalTemplate
from ...ops.utils import draw_pre, draw_post, draw_nurbs_curve
import bmesh

def draw_move_object_callback_px(self, context):
    draw_pre(width=2)

    for curve in self.draw_curves:
        draw_nurbs_curve(curve, color=(1, 0, 0, self.alpha))

    draw_post()


class ADJT_OT_ExtractEdgeAsCurve(ADJT_OT_ModalTemplate):
    """Extract edge to curve in edit mode
将在编辑模式选中边转换为曲线"""
    bl_idname = 'mesh.adjt_extract_edge_as_curve'
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
        # ori_obj.name = 'Curve from ' + ori_obj.name

        # new_obj = copy_obj(ori_obj)
        bm = bmesh.from_edit_mesh(ori_obj.data).copy()
        geo_type = getattr(bm, 'edges')
        deselect_geom = [elem for elem in geo_type if not elem.select]

        if deselect_geom:
            bmesh.ops.delete(bm, geom=deselect_geom, context='EDGES')

        new_mesh = ori_obj.data.copy()
        new_mesh.name = F"{ori_obj.data.name}_edges"
        bm.to_mesh(new_mesh)
        bm.free()

        new_obj = ori_obj.copy()
        new_obj.modifiers.clear()
        new_obj.name = f"{ori_obj.name}_{'Copy'}"
        new_obj.data = new_mesh

        context.collection.objects.link(new_obj)
        context.view_layer.objects.active = new_obj

        new_obj.select_set(1)
        ori_obj.select_set(0)

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='CURVE')

        # set nurbs type
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.spline_type_set(type='NURBS')
        bpy.ops.object.mode_set(mode='OBJECT')

        curve = context.active_object
        curve.data.splines[0].use_endpoint_u = True

        self.tips.clear()
        self.tips.append('')
        self.tips.append(f'"{ori_obj.name}" has been extract')

        self.draw_curves.clear()
        self.draw_curves.append(curve)

        self._finish = True


def register():
    bpy.utils.register_class(ADJT_OT_ExtractEdgeAsCurve)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ExtractEdgeAsCurve)
