import bpy
from bpy.props import StringProperty, EnumProperty


class ADJT_OT_ClipBoard(bpy.types.Operator):
    """Copy to clipboard
复制到剪切板"""
    bl_idname = 'adjt.clip_board'
    bl_label = 'Copy'

    data: StringProperty(default='Nothing is copied')

    def execute(self, context):
        context.window_manager.clipboard = self.data
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ADJT_OT_ClipBoard)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ClipBoard)
