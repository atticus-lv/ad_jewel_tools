import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from ..ops_utils.op_template import ADJT_OT_ModalTemplate


class ADJT_OT_Array(ADJT_OT_ModalTemplate):
    '''apply Preset
应用预设'''
    bl_label = "Array Preset"
    bl_idname = "node.adjt_array"
    bl_options = {'UNDO_GROUPED'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Circular Array')

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and context.active_object.type in {'CURVE','MESH'}

    def main(self, context):
        self.display_ob = context.active_object
        mod = self.display_ob.modifiers.new(name='ADJT_Array_modifier', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)

        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Apply "{self.node_group_name}" preset')

        self._finish = True

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'array.blend')

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
    bpy.utils.register_class(ADJT_OT_Array)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_Array)
