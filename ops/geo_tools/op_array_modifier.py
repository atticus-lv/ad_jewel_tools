import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from .PresetTemplate import PresetTemplate


class ADJT_OT_Array(PresetTemplate):
    '''Apply Array Preset
应用阵列预设'''
    bl_label = "Array Preset"
    bl_idname = "node.adjt_array"
    bl_options = {'UNDO_GROUPED'}

    filter = {'CURVE', 'MESH'}
    # preset information
    modifier_name = 'ADJT_Array_modifier'
    version = '1.0'
    dir_name = 'node_groups'
    file_name = 'array.blend'
    node_group_name: StringProperty(name='Node Group Name', default='Circular Array')

    # action
    create_new_obj = False


def register():
    bpy.utils.register_class(ADJT_OT_Array)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_Array)
