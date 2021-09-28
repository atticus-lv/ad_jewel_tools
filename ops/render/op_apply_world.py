import os.path

from bpy.props import EnumProperty
from ..utils import ADJT_NodeTree
import os
import math


def get_hdr_list() -> tuple[list[str], list[str], str, str]:
    # build-in
    bl_dir = os.path.join(bpy.utils.system_resource('DATAFILES'), 'studiolights', 'world')
    # user
    user_dir = os.path.join(bpy.utils.user_resource('DATAFILES'), 'studiolights', 'world')

    bl_image_list = [file for file in os.listdir(bl_dir)]
    user_image_list = [file for file in os.listdir(user_dir)] if os.path.isdir(user_dir) else []

    return bl_image_list, user_image_list, bl_dir, user_dir


def load_image(image_node, dir, image_name):
    # load img
    image = bpy.data.images.get(image_name)
    if not image:
        image = bpy.data.images.load(filepath=os.path.join(dir, image_name))
    try:
        image_node.image = image
        return os.path.join(dir, image_name)
    except Exception as e:
        print(e)
        return


# work with ssm
def init_world_nodes(context):
    if context.scene.world is None:
        world = bpy.data.worlds.new('World')
        context.scene.world = world

    world_nt = ADJT_NodeTree(context.scene.world.node_tree)
    world_out_put = world_nt.get_node("World Output")

    # init nodes
    node_background = world_nt.get_node("SSM_BG")
    node_hdr_image = world_nt.get_node("SSM_Hdr_Image")
    node_hsv = world_nt.get_node("SSM_HSV")
    node_uv_map = world_nt.get_node("SSM_Mapping")
    node_tex_C = world_nt.get_node("SSM_Tc")

    node_rotate_x = world_nt.get_node("SSM_Rv_x")
    node_rotate_y = world_nt.get_node("SSM_Rv_y")
    node_rotate_z = world_nt.get_node("SSM_Rv")

    node_convert_radians_z = world_nt.get_node("SSM_Cv")
    node_convert_radians_x = world_nt.get_node("SSM_Cv_x")
    node_convert_radians_y = world_nt.get_node("SSM_Cv_y")

    node_combine_xyz = world_nt.get_node("SSM_Cv2")

    # if world_out_put is None:
    #     world_out_put = nt.add_node()

    if node_background is None:
        node_background = world_nt.add_node("ShaderNodeBackground", name="SSM_BG")

    if node_hdr_image is None:
        node_hdr_image = world_nt.add_node("ShaderNodeTexEnvironment", name="SSM_Hdr_Image")

    if node_hsv is None:
        node_hsv = world_nt.add_node("ShaderNodeHueSaturation", name="SSM_HSV")

    if node_uv_map is None:
        node_uv_map = world_nt.add_node("ShaderNodeMapping", name="SSM_Mapping")

    if node_tex_C is None:
        node_tex_C = world_nt.add_node("ShaderNodeTexCoord", name="SSM_Tc")

    if node_rotate_x is None:
        node_rotate_x = world_nt.add_node("ShaderNodeValue", name="SSM_Rv_x")

    if node_rotate_y is None:
        node_rotate_y = world_nt.add_node("ShaderNodeValue", name="SSM_Rv_y")

    if node_rotate_z is None:
        node_rotate_z = world_nt.add_node("ShaderNodeValue", name="SSM_Rv")

    if node_convert_radians_x is None:
        node_convert_radians_x = world_nt.add_node("ShaderNodeMath", name="SSM_Cv_x")

    if node_convert_radians_y is None:
        node_convert_radians_y = world_nt.add_node("ShaderNodeMath", name="SSM_Cv_y")

    if node_convert_radians_z is None:
        node_convert_radians_z = world_nt.add_node("ShaderNodeMath", name="SSM_Cv")

    if node_combine_xyz is None:
        node_combine_xyz = world_nt.add_node("ShaderNodeCombineXYZ", name="SSM_Cv2")

    # set location
    node_background.location = (200, 100)
    node_hsv.location = (0, 100)
    node_hdr_image.location = (-300, 100)
    node_uv_map.location = (-500, 100)
    node_tex_C.location = (-700, 100)

    node_rotate_x.location = (-1100, 0)
    node_rotate_y.location = (-1100, -100)
    node_rotate_z.location = (-1100, -200)

    node_rotate_y.outputs[0].default_value = node_rotate_x.outputs[0].default_value = \
        node_rotate_z.outputs[0].default_value = 0

    node_convert_radians_x.location = (-900, 0)
    node_convert_radians_y.location = (-900, -150)
    node_convert_radians_z.location = (-900, -300)

    node_convert_radians_z.operation = node_convert_radians_x.operation = node_convert_radians_y.operation = 'RADIANS'

    node_combine_xyz.location = (-700, -200)

    # link
    world_nt.link_node(node_rotate_x.outputs[0], node_convert_radians_x.inputs[0])
    world_nt.link_node(node_convert_radians_x.outputs[0], node_combine_xyz.inputs[0])

    world_nt.link_node(node_rotate_y.outputs[0], node_convert_radians_y.inputs[0])
    world_nt.link_node(node_convert_radians_y.outputs[0], node_combine_xyz.inputs[1])

    world_nt.link_node(node_rotate_z.outputs[0], node_convert_radians_z.inputs[0])
    world_nt.link_node(node_convert_radians_z.outputs[0], node_combine_xyz.inputs[2])

    world_nt.link_node(node_combine_xyz.outputs[0], node_uv_map.inputs[2])

    world_nt.link_node(node_background.outputs[0], world_out_put.inputs[0])
    world_nt.link_node(node_hdr_image.outputs[0], node_hsv.inputs[4])
    world_nt.link_node(node_hsv.outputs[0], node_background.inputs[0])
    world_nt.link_node(node_uv_map.outputs[0], node_hdr_image.inputs[0])
    world_nt.link_node(node_tex_C.outputs[0], node_uv_map.inputs[0])

    return node_hdr_image, node_background, node_rotate_z


import bpy
from ..ops_utils.op_template import ADJT_OT_ModalTemplate


class ADJT_OT_InitShading(ADJT_OT_ModalTemplate):
    bl_label = "Init Shading"
    bl_idname = "render.adjt_init_shading"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def main(self, context):
        view = context.space_data
        shading = view.shading if view.type == 'VIEW_3D' else context.scene.display.shading
        shading.use_scene_world_render = False
        shading.type = 'RENDERED'
        self._finish = True


# class ADJT_OT_InitShading(ADJT_OT_NormalTemplate):
#     bl_label = "Init Shading"
#     bl_idname = "render.adjt_init_shading"
#     bl_options = {"REGISTER", "UNDO", "INTERNAL"}
#
#     def execute(self, context):
#     # def main(self, context):
#         view = context.space_data
#         shading = view.shading if view.type == 'VIEW_3D' else context.scene.display.shading
#         shading.use_scene_world_render = False
#         shading.type = 'RENDERED'
#         # self._finish = True
#         self.draw_ui(context,title=self.bl_label,tips=[])
#         return {"FINISHED"}

class ADJT_OT_ApplyWorld(ADJT_OT_ModalTemplate):
    '''Apply View Setting to World
应用预览至世界'''
    bl_label = "Apply World"
    bl_idname = "adjt.apply_world"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    tips = ['']

    def main(self, context):
        view = context.space_data
        shading = view.shading if view.type == 'VIEW_3D' else context.scene.display.shading

        cur_hdr = shading.studio_light

        bl_img_list, user_img_list, bl_dir, user_dir = get_hdr_list()
        node_hdr_image, node_background, node_rotate_z = init_world_nodes(context)

        node_rotate_z.outputs[0].default_value = math.degrees(shading.studiolight_rotate_z)
        node_background.inputs[1].default_value = shading.studiolight_intensity

        if cur_hdr in bl_img_list:
            ans = load_image(node_hdr_image, dir=bl_dir, image_name=cur_hdr)
            from_user = False
        elif cur_hdr in user_img_list:
            ans = load_image(node_hdr_image, dir=user_dir, image_name=cur_hdr)
            from_user = True
        else:
            ans = False

        if ans:
            self.tips.clear()
            self.tips.append('')
            self.tips.append(f'Load {cur_hdr} from {"User" if from_user else "Blender"}')
            context.scene.adjt_world_mode = 'RENDER'
        else:
            self.tips.clear()
            self.tips.append('')
            self.tips.append('Load Image Failed')

        self._finish = True


def update_world_mode(self, context):
    view = context.space_data
    shading = view.shading if view.type == 'VIEW_3D' else context.scene.display.shading
    shading.use_scene_world_render = False if context.scene.adjt_world_mode == 'PREVIEW' else True


def register():
    bpy.utils.register_class(ADJT_OT_ApplyWorld)
    bpy.utils.register_class(ADJT_OT_InitShading)
    bpy.types.Scene.adjt_world_mode = EnumProperty(name='World Mode', items=[
        ('PREVIEW', 'Preview', ''),
        ('RENDER', 'Render', '')],
                                                   default='PREVIEW', update=update_world_mode)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ApplyWorld)
    bpy.utils.unregister_class(ADJT_OT_InitShading)
