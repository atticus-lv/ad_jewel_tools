import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from ..ops_utils.Template import ADJT_OT_ModalTemplate


class PresetTemplate(ADJT_OT_ModalTemplate):
    bl_options = {'UNDO_GROUPED'}

    # filter
    filter = {'MESH'}
    # preset information
    modifier_name = 'ADJT_Template'
    version = '1.0'
    dir_name = 'node_groups'
    file_name = 'array.blend'
    node_group_name: StringProperty(name='Node Group Name')

    # action
    create_new_obj = False
    # data
    display_ob = None

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and context.active_object.type in self.filter

    def main(self, context):
        self.apply_preset(context)
        self.append_tips()

        self._finish = True

    def refresh_modifier_hack(self,mod):
        # refresh
        mod.show_viewport = False
        mod.show_viewport = True

    def init_geo_mod(self,mod):
        src_ng = mod.node_group
        if src_ng: bpy.data.node_groups.remove(src_ng)

    def apply_preset(self, context):
        self.display_ob = context.active_object if not self.create_new_obj else self.create_obj()

        mod = self.display_ob.modifiers.new(name=self.modifier_name, type='NODES')
        src_ng = mod.node_group
        if src_ng: bpy.data.node_groups.remove(src_ng)
        mod.node_group = self.get_preset(dir_name=self.dir_name, file_name=self.file_name,
                                         node_group_name=self.node_group_name + f' {self.version}')

    def append_tips(self):
        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Apply "{self.node_group_name}" preset')

    def create_obj(self):
        vertices = edges = faces = []
        new_mesh = bpy.data.meshes.new('adjt_empty_mesh')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        obj = bpy.data.objects.new('new_object', new_mesh)
        bpy.context.collection.objects.link(obj)

        return obj

    def get_preset(self, dir_name, file_name, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                dir_name, file_name)

        if node_group_name in bpy.data.node_groups:
            preset_node = bpy.data.node_groups[node_group_name]
        else:
            with bpy.data.libraries.load(base_dir, link=False) as (data_from, data_to):
                data_to.node_groups = [name for name in data_from.node_groups if name == node_group_name]

            preset_node = data_to.node_groups[0]

        return preset_node
