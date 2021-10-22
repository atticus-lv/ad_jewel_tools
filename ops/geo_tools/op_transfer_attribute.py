import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from .PresetTemplate import PresetTemplate


class ADJT_OT_TransferAttribute(PresetTemplate):
    '''Apply Array Preset
应用阵列预设'''
    bl_label = "Transfer Attribute"
    bl_idname = "node.transfer_attribute"
    bl_options = {'UNDO_GROUPED'}

    filter = {'CURVE', 'MESH'}
    # preset information
    modifier_name = 'ADJT_TransferAttribute'
    version = '1.0'
    dir_name = 'node_groups'
    file_name = 'utils.blend'
    node_group_name: StringProperty(name='Node Group Name', default='Transfer Attribute')

    # action
    create_new_obj = False


def register():
    bpy.utils.register_class(ADJT_OT_TransferAttribute)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_TransferAttribute)
