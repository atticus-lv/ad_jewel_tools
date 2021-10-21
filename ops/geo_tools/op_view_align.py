import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from .PresetTemplate import PresetTemplate


class ADJT_OT_ViewAlign(PresetTemplate):
    '''Apply Align Preset
应用摆放预设'''
    bl_label = "View Align"
    bl_idname = "node.adjt_view_align"
    bl_options = {'UNDO_GROUPED'}

    version = 'v1'
    modifier_name = 'ADJT_ViewAlign'
    dir_name = 'node_groups'
    file_name = 'view_align_preset.blend'

    node_group_name: StringProperty(name='Node Group Name', default='Horizontal 4 View')

    # action
    create_new_obj = False

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and hasattr(context.active_object, 'modifiers')

    def apply_preset(self, context):
        self.display_ob = context.active_object if not self.create_new_obj else self.create_obj()

        mod = self.display_ob.modifiers.new(name=self.modifier_name, type='NODES')
        self.init_geo_mod(mod)
        mod.node_group = self.get_preset(dir_name=self.dir_name, file_name=self.file_name,
                                         node_group_name=self.node_group_name)



def register():
    bpy.utils.register_class(ADJT_OT_ViewAlign)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ViewAlign)
