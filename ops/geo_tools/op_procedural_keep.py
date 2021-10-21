import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__
import bmesh

from ..ops_utils.Template import ADJT_OT_ModalTemplate


class ADJT_OT_ProceduralKeep(bpy.types.Operator):
    """Procedural Delete in Edit mode
程序化删除编辑模式下的选中项"""
    bl_idname = 'mesh.adjt_procedural_keep'
    bl_label = 'Delete / Keep Faces'
    bl_options = {'UNDO_GROUPED'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Procedural Keep')

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'

    def execute(self, context):
        self.display_ob = context.active_object
        me = self.display_ob.data
        bm = bmesh.from_edit_mesh(me)
        # select invert
        verts = [i for i, v in enumerate(bm.verts) if v.select is False]

        # add vertex group
        bpy.ops.object.mode_set(mode='OBJECT')
        vertex_group = self.display_ob.vertex_groups.new(name="Selected Invert")
        vertex_group.add(verts, 1.0, 'ADD')

        # mode modifier
        mod = self.display_ob.modifiers.new(name='ADJT_ProceduralKeep', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)

        mod.show_on_cage = True
        mod["Input_2_use_attribute"] = True
        mod["Input_2_attribute_name"] = vertex_group.name

        # refresh
        mod.show_viewport = False
        mod.show_viewport = True

        bpy.ops.object.select_all(action='DESELECT')
        self.display_ob.select_set(True)
        context.view_layer.objects.active = self.display_ob

        return {'FINISHED'}

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'utils.blend')

        node_group_dir = os.path.join(base_dir, 'NodeTree') + '/'

        if node_group_name in bpy.data.node_groups:
            preset_node = bpy.data.node_groups[node_group_name]
        else:
            bpy.ops.wm.append(filename=node_group_name, directory=node_group_dir)
            preset_node = bpy.data.node_groups[node_group_name]

        # with bpy.data.libraries.load(base_dir, link=False) as (data_from, data_to):
        #     data_to.node_groups = [name for name in data_from.node_groups if name == node_group_name]
        #
        # preset_node = data_to.node_groups[0]

        return preset_node


def register():
    bpy.utils.register_class(ADJT_OT_ProceduralKeep)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ProceduralKeep)
