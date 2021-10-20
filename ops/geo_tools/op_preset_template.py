import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from ..ops_utils.op_template import ADJT_OT_ModalTemplate


class PresetTemplate(ADJT_OT_ModalTemplate):
    bl_options = {'UNDO_GROUPED'}

    filter = {'MESH'}
    file = 'animate_preset.blend'
    node_group_name: StringProperty(name='Node Group Name')

    # put modifier on an other object
    create_new_obj = False
    display_ob = None

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and context.active_object.type in self.filter

    def create_obj(self):
        vertices = edges = faces = []
        new_mesh = bpy.data.meshes.new('adjt_empty_mesh')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        obj = bpy.data.objects.new('new_object', new_mesh)
        bpy.context.collection.objects.link(obj)

        return obj

    def main(self, context):
        self.display_ob = context.active_object if not self.create_new_obj else self.create_obj()

        mod = self.display_ob.modifiers.new(name='ADJT_Animate', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)

        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Apply "{self.node_group_name}" preset')

        bpy.ops.screen.animation_play("INVOKE_DEFAULT")

        self._finish = True

    def get_preset(self, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups', self.file)

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
