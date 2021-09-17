import bpy
import os

from .. import __folder_name__


class ADJT_OT_ViewAlign(bpy.types.Operator):
    '''Copy the select obj to align view
选择并复制当前物体为三视图'''
    bl_label = "视图摆放"
    bl_idname = "adjt.view_align"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'

    def execute(self, context):
        ob = context.active_object
        mod = ob.modifiers.new(name='ViewAlign', type='NODES')
        mod.node_group = self.get_preset(node_group_name='三视图_横向排布')

        # if 'View Align Dep' not in context.scene.collection.children:
        #     dep_coll_dir = bpy.data.collections.new("View Align Dep")
        #     context.scene.collection.children.link(dep_coll_dir)
        # else:
        #     dep_coll_dir = context.scene.collection.children['View Align Dep']

        return {"FINISHED"}

    def get_preset(sellf, node_group_name='三视图_横向排布'):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'view_align',
                                'view_align_preset.blend')

        node_group_dir = os.path.join(base_dir, 'NodeTree') + '/'

        if node_group_name in bpy.data.node_groups:
            preset_node = bpy.data.node_groups[node_group_name]
        else:
            bpy.ops.wm.append(filename=node_group_name, directory=node_group_dir)
            preset_node = bpy.data.node_groups[node_group_name]

        return preset_node


def register():
    bpy.utils.register_class(ADJT_OT_ViewAlign)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ViewAlign)
