import bpy
from ..ops_utils.Template import ADJT_OT_ModalTemplate

import os

class ADJT_OT_InitThumb(ADJT_OT_ModalTemplate):

    bl_label = "Init Thumb"
    bl_idname = "adjt.init_thumb"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def main(self, context):
        dir = os.path.dirname(bpy.app.binary_path).replace('\\','/')
        cmd = f'cd {dir} & Blender -R'
        ans = os.popen(cmd).read()
        print(ans)

        self._finish = True

def register():
    bpy.utils.register_class(ADJT_OT_InitThumb)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_InitThumb)