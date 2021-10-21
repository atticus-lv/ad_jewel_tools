import bpy
import os
from bpy.props import StringProperty, PointerProperty, IntProperty
from ... import __folder_name__
import bmesh

from ..ops_utils.Template import ADJT_OT_ModalTemplate


class ADJT_UL_MatList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon_value=icon)

            row = row.row(align=True)
            row.alignment = 'RIGHT'
            if item.use_fake_user:
                row.label(text="F")
            else:
                row.label(text=str(item.users))

        elif self.layout_type in {'GRID'}:
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)


class ADJT_OT_SetMaterial(ADJT_OT_ModalTemplate):
    """Procedural Delete in Edit mode"""
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = 'mesh.adjt_set_material'
    bl_label = 'Set Material'

    node_group_name = 'Set Material'

    object = None
    display_ob = None

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type in {'MESH', 'CURVE', 'FONT'}

    def main(self, context):
        self.display_ob = context.active_object

        # mode modifier
        mod = self.display_ob.modifiers.new(name='ADJT_SetMaterial', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)

        mod["Input_2"] = context.window_manager.adjt_tmp_mat
        # refresh
        mod.show_viewport = False
        mod.show_viewport = True

        self._finish = True

        return {'FINISHED'}

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'material.blend')

        if node_group_name in bpy.data.node_groups:
            preset_node = bpy.data.node_groups[node_group_name]
        else:
            with bpy.data.libraries.load(base_dir, link=False) as (data_from, data_to):
                data_to.node_groups = [name for name in data_from.node_groups if name == node_group_name]

            preset_node = data_to.node_groups[0]

        return preset_node


def register():
    bpy.types.WindowManager.adjt_tmp_mat = PointerProperty(name='Tmp Mat Pv', type=bpy.types.Material)

    bpy.utils.register_class(ADJT_UL_MatList)
    bpy.utils.register_class(ADJT_OT_SetMaterial)


def unregister():
    del bpy.types.WindowManager.adjt_tmp_mat

    bpy.utils.unregister_class(ADJT_UL_MatList)
    bpy.utils.unregister_class(ADJT_OT_SetMaterial)
