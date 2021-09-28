import bpy
import os
from bpy.props import StringProperty, EnumProperty, BoolProperty
from ...preferences import get_pref


def add_path_to_recent_files(path):
    try:
        recent_path = os.path.join(bpy.utils.user_resource('CONFIG'), 'recent-files.txt')

        with open(recent_path, "r+") as f:
            content = f.read()
            f.seek(0, 0)
            f.write(path.rstrip('\r\n') + '\n' + content)

    except (IOError, OSError, FileNotFoundError):
        pass


class ADJT_OT_LoadFile(bpy.types.Operator):
    """Load Files in current directory"""
    bl_idname = "wm.adjt_load_file"
    bl_label = "Load File"
    bl_options = {'REGISTER'}

    action: EnumProperty(name='Action', items=[
        ('-1', 'Previous', ''),
        ('+1', 'Next', ''),
    ])

    @classmethod
    def poll(cls, context):
        return bpy.data.filepath

    def execute(self, context):
        load_ui = get_pref().load_ui
        cur_path = os.path.dirname(bpy.data.filepath)
        cur_blend = os.path.basename(bpy.data.filepath)

        file_list = [f for f in sorted(os.listdir(cur_path)) if f.endswith(".blend")]

        index = file_list.index(cur_blend)

        target_id = index + eval(self.action)

        if target_id < 0:
            target_id = len(file_list) - 1
        elif target_id > len(file_list) - 1:
            target_id = 0

        blend_path = os.path.join(cur_path, file_list[target_id])
        add_path_to_recent_files(blend_path)
        bpy.ops.wm.open_mainfile(filepath=blend_path, load_ui=load_ui)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ADJT_OT_LoadFile)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_LoadFile)
