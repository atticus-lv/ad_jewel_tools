import bpy
import os
from bpy.props import IntProperty, EnumProperty

from .. import __folder_name__


class ADJT_OT_CamFrame(bpy.types.Operator):
    '''Select the object you want to add frame camera
选择你想要添加的框选相机的物体'''
    bl_label = "生成框选相机"
    bl_idname = "adjt.cam_frame"
    bl_options = {"REGISTER", "UNDO"}

    length: IntProperty(name='Focal Length', description="Camera Focal length",
                        default=300, min=1, soft_max=300)

    safe_pixel: IntProperty(name='Safe area pixel', description="Empty area for the selection and camera frame",
                            default=50)

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.mode == 'OBJECT'

    def execute(self, context):
        ori_select = context.selected_objects

        # add cam and correct viewport
        bpy.ops.object.camera_add()
        cam = context.object
        context.scene.camera = cam

        cam.data.lens = self.length
        cam.data.show_name = True

        context.area.spaces[0].region_3d.view_perspective = 'PERSP'
        override = {'area': context.area,
                    'region': [region for region in context.area.regions if region.type == "WINDOW"][0]}
        bpy.ops.view3d.camera_to_view(override)

        # set frame obj
        cam.select_set(0)
        for obj in ori_select:
            obj.select_set(1)

        # set safe area
        ori_res_x = context.scene.render.resolution_x
        ori_res_y = context.scene.render.resolution_y

        context.scene.render.resolution_y = ori_res_x
        context.scene.render.resolution_x -= self.safe_pixel * 2

        bpy.ops.view3d.camera_to_view_selected()

        # restore
        context.scene.render.resolution_x = ori_res_x
        context.scene.render.resolution_y = ori_res_y

        return {"FINISHED"}


def register():
    bpy.utils.register_class(ADJT_OT_CamFrame)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_CamFrame)
