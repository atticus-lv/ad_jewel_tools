import bpy
import os
from bpy.props import StringProperty
from .. import __folder_name__

from .op_utils import ADJT_OT_ModalTemplate


class ADJT_OT_ViewAlign(ADJT_OT_ModalTemplate):
    '''Copy the select obj to align view
选择并复制当前物体为三视图'''
    bl_label = "View Align"
    bl_idname = "adjt.view_align"
    bl_options = {"REGISTER", "UNDO"}

    object = None
    node_group_name: StringProperty(name='Node Group Name', default='四视图_横向排布')

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'

    def main(self, context):
        # set and hide origin obj
        self.object = context.active_object
        self.object.hide_render = 1
        self.object.hide_set(True)

        # extra ob for display
        bpy.ops.mesh.primitive_plane_add()
        ob = context.active_object
        ob.name = 'ADJT_Render'
        mod = ob.modifiers.new(name='ViewAlign', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)
        if 'View Align Dep' not in context.scene.collection.children:
            dep_coll_dir = bpy.data.collections.new("View Align Dep")
            context.scene.collection.children.link(dep_coll_dir)
        else:
            dep_coll_dir = context.scene.collection.children['View Align Dep']

        context.collection.objects.unlink(ob)
        dep_coll_dir.objects.link(ob)

        # set obj
        nt = mod.node_group
        node = nt.nodes.get('Group')
        ob_ip = node.inputs.get('Object')
        ob_ip.default_value = self.object

        # set active
        context.view_layer.objects.active = ob

        self._finish = True

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
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
