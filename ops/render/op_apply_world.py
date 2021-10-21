import os.path

from ... import __folder_name__
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
    if not image or not image.has_data:
        image = bpy.data.images.load(filepath=os.path.join(dir, image_name))
    try:
        image_node.image = image
        return os.path.join(dir, image_name)
    except Exception as e:
        print(e)
        return


def init_world_nodes(context, node_group_name='adjt_quick_world'):
    if context.scene.world is None:
        world = bpy.data.worlds.new('World')
        context.scene.world = world

    nt = context.scene.world.node_tree
    output_node = [node for node in nt.nodes if node.bl_idname == 'ShaderNodeOutputWorld'][0]

    group_node = nt.nodes.get('Group')
    if group_node is None or not hasattr(group_node,'node_tree') or group_node.node_tree.name != 'adjt_quick_world':
        group_node = nt.nodes.new('ShaderNodeGroup')
        group_node.name = 'Group'

    base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                            'node_groups', 'world.blend')

    if node_group_name in bpy.data.node_groups:
        preset_node = bpy.data.node_groups[node_group_name]
    else:
        with bpy.data.libraries.load(base_dir, link=False) as (data_from, data_to):
            data_to.node_groups = [name for name in data_from.node_groups if name == node_group_name]

        preset_node = data_to.node_groups[0]

    group_node.node_tree = preset_node
    image_node = preset_node.nodes.get('Image')

    nt.links.new(group_node.outputs[0],output_node.inputs['Surface'])

    return group_node, image_node


import bpy
from ..ops_utils.Template import ADJT_OT_ModalTemplate


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
        group_node, node_hdr_image = init_world_nodes(context)

        group_node.inputs['Rotation'].default_value[2] = math.degrees(shading.studiolight_rotate_z)
        group_node.inputs['BG Strength'].default_value = shading.studiolight_intensity

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
