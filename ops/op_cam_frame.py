import bpy
import os
from bpy.props import IntProperty, EnumProperty, BoolProperty

from .op_utils import ADJT_OT_ModalTemplate
from .. import __folder_name__


class ADJT_OT_CamFrame(ADJT_OT_ModalTemplate):
    '''Select the object you want to add frame camera
选择你想要添加的框选相机的物体'''
    bl_label = "Frame Camera"
    bl_idname = "adjt.cam_frame"
    bl_options = {"REGISTER", "UNDO"}

    tips = [
        '',
        'Ready for Render'
    ]

    safe_pixel: IntProperty(name='Safe area pixel', description="Empty area for the selection and camera frame",
                            default=50)
    use_bound: BoolProperty(name='Add Boundary', default=False)

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.mode == 'OBJECT' and context.active_object.type == 'MESH'

    def main(self, context):
        if context.scene.render.resolution_x < context.scene.render.resolution_y:
            self.tips.append("ERROR: 'Only work when resolution X > resolution Y'")
            self._cancel = True

        # use bound geo nodes to measure instances
        self.use_bound = False
        for n in context.active_object.dimensions:
            if n == 0:
                self.use_bound = True
                break

        ori_select = context.active_object

        # add bound
        mod = None
        if self.use_bound:
            mod = ori_select.modifiers.new(name='ViewAlign', type='NODES')
            mod.node_group = self.get_preset(node_group_name='adjt_bound')

        # add cam and correct viewport
        camera_data = bpy.data.cameras.new(name='Camera')
        cam = bpy.data.objects.new('Camera', camera_data)
        context.scene.collection.objects.link(cam)
        context.scene.camera = cam

        cam.data.type = 'ORTHO'
        cam.data.show_name = True

        context.area.spaces[0].region_3d.view_perspective = 'PERSP'
        override = {'area': context.area,
                    'region': [region for region in context.area.regions if region.type == "WINDOW"][0]}
        bpy.ops.view3d.camera_to_view(override)

        # set frame obj
        cam.select_set(0)
        ori_select.select_set(1)

        # set safe area
        safe_scale = self.safe_pixel * 2 / context.scene.render.resolution_x

        bpy.ops.view3d.camera_to_view_selected()  # center the objects
        # if cam on x axis then measure the x axis dimension
        size = ori_select.dimensions[1] if cam.location[1] > cam.location[0] else ori_select.dimensions[0]
        cam.data.ortho_scale = (1 + safe_scale) * size

        # remove modifiers
        if mod:
            ori_select.modifiers.remove(mod)
            self.use_bound = False # prevent crash

        self._finish = True

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'view_align_preset.blend')

        node_group_dir = os.path.join(base_dir, 'NodeTree') + '/'

        if node_group_name in bpy.data.node_groups:
            preset_node = bpy.data.node_groups[node_group_name]
        else:
            bpy.ops.wm.append(filename=node_group_name, directory=node_group_dir)
            preset_node = bpy.data.node_groups[node_group_name]

        return preset_node


def register():
    bpy.utils.register_class(ADJT_OT_CamFrame)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_CamFrame)
