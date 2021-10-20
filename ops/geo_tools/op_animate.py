import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from ..ops_utils.op_template import ADJT_OT_ModalTemplate


class ADJT_OT_Animate(ADJT_OT_ModalTemplate):
    '''Copy the select mesh to apply animation
选择并复制应用预设动画'''
    bl_label = "Animate"
    bl_idname = "node.adjt_animate"
    bl_options = {'UNDO_GROUPED'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Turn Table')

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'

    def main(self, context):
        self.display_ob = context.active_object
        mod = self.display_ob.modifiers.new(name='ADJT_Animate', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)

        # refresh because of unfixed bug
        mod.show_viewport = False
        mod.show_viewport = True
        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Apply "{self.node_group_name}" preset')

        bpy.ops.screen.animation_play("INVOKE_DEFAULT")

        self._finish = True

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'animate_preset.blend')

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
    bpy.utils.register_class(ADJT_OT_Animate)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_Animate)
