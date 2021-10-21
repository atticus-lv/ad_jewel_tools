import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from ..ops_utils.Template import ADJT_OT_ModalTemplate


class ADJT_OT_CurveScatter(ADJT_OT_ModalTemplate):
    '''apply Preset
应用预设'''
    bl_label = "Scatter Along Curve"
    bl_idname = "node.curve_scatter"
    bl_options = {'UNDO_GROUPED'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Scatter along curve')


    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'CURVE' and len(context.selected_objects) == 2

    def main(self, context):
        self.ori_curve = context.active_object
        self.ori_mesh = [obj for obj in context.selected_objects if obj != self.ori_curve][0]

        mod = self.ori_mesh.modifiers.new(name='ADJT_scatter_along_curve', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)
        mod['Input_2'] = self.ori_curve

        # refresh because of unfixed bug
        mod.show_viewport = False
        mod.show_viewport = True

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
    bpy.utils.register_class(ADJT_OT_CurveScatter)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_CurveScatter)
