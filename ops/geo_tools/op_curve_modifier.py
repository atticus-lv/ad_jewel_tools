import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from .PresetTemplate import PresetTemplate


class ADJT_OT_Curve(PresetTemplate):
    '''Apply Curve Preset
应用曲线预设'''
    bl_label = "Curve Preset"
    bl_idname = "node.adjt_curve"
    bl_options = {'UNDO_GROUPED'}

    filter = {'CURVE', 'FONT'}
    # preset information
    modifier_name = 'ADJT_Curve_modifier'
    version = '1.1'
    dir_name = 'node_groups'
    file_name = 'array.blend'
    node_group_name: StringProperty(name='Node Group Name', default='MS')
    # action
    create_new_obj = False


def register():
    bpy.utils.register_class(ADJT_OT_Curve)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_Curve)
