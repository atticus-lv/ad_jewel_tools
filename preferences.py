import bpy
import os
from bpy.props import (EnumProperty,
                       StringProperty,
                       BoolProperty,
                       CollectionProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty)
from bpy.types import PropertyGroup

import webbrowser

from .ui.t3dn_bip import previews
from .ui.utils import t3dn_bip_convert
from . import __folder_name__


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


# Image items
####################

__tempPreview__ = {}  # store in global, delete in unregister

# image_extensions = ('.png', '.jpg', '.jpeg')
image_extensions = ('.bip')


def check_extension(input_string: str, extensions: set) -> bool:
    for ex in extensions:
        if input_string.endswith(ex): return True


def clear_preview_cache():
    for preview in __tempPreview__.values():
        previews.remove(preview)
    __tempPreview__.clear()


def enum_thumbnails_from_dir_items(prop_list, prop_index, context):
    enum_items = []
    if context is None: return enum_items

    try:
        item = prop_list[prop_index]
        directory = item.path
    except(Exception):
        directory = ""

    # store
    image_preview = __tempPreview__["adjt_thumbnails"]

    if directory == image_preview.img_dir:
        return image_preview.img

    if directory and os.path.exists(directory):
        image_names = []
        for fn in os.listdir(directory):
            if check_extension(fn.lower(), image_extensions):
                image_names.append(fn)

        for i, name in enumerate(image_names):
            filepath = os.path.join(directory, name)

            icon = image_preview.get(name)
            if not icon:
                thumbnail = image_preview.load(name, filepath, 'IMAGE')
            else:
                thumbnail = image_preview[name]
            enum_items.append((name, name, "", thumbnail.icon_id, i))  # item: sign,display,description,icon,index

    image_preview.img = enum_items
    image_preview.img_dir = directory

    return image_preview.img


def enum_view_align_preset_item(self, context):
    pref = get_pref()
    return enum_thumbnails_from_dir_items(pref.view_align_preset_list, pref.view_align_preset_list_index, context)


def enum_animate_preset(self, context):
    pref = get_pref()
    return enum_thumbnails_from_dir_items(pref.anim_preset_list, pref.anim_preset_list_index, context)


def update_path_name2(self, context):
    full_dir_name = os.path.dirname(self.path) if os.path.isdir(self.path) else None
    if full_dir_name is None: return None
    self.name = full_dir_name.replace('\\', '/').split('/')[-1]


class ViewAlignThumbProperty(PropertyGroup):
    name: StringProperty(name='name')
    path: StringProperty(name='dir', description='folder dir', subtype='DIR_PATH', update=update_path_name2)
    thumbnails: EnumProperty(name='thumb', items=enum_view_align_preset_item)


class AnimateThumProperty(PropertyGroup):
    name: StringProperty(name='name')
    path: StringProperty(name='dir', description='folder dir', subtype='DIR_PATH', update=update_path_name2)
    thumbnails: EnumProperty(name='thumb', items=enum_animate_preset)


from .ui.t3dn_bip.ops import InstallPillow


class T3DN_OT_bip_showcase_install_pillow(bpy.types.Operator, InstallPillow):
    bl_idname = 't3dn.bip_showcase_install_pillow'


# Preference
####################

class ADJT_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    load_ui: BoolProperty(name='Load UI')

    view_align_preset_list: CollectionProperty(type=ViewAlignThumbProperty)
    view_align_preset_list_index: IntProperty(default=0, min=0, name='Active')

    anim_preset_list: CollectionProperty(type=AnimateThumProperty)
    anim_preset_list_index: IntProperty(default=0, min=0, name='Active')

    # ui
    use_workflow_panel: BoolProperty(name='Use Workflow Panel', default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'use_workflow_panel')
        # layout.operator('t3dn.bip_showcase_install_pillow', text='安装Pillow（加快预览加载）')


def init_thumb(prop, prop_index, sub_dir):
    pref = get_pref()

    img_list = getattr(pref, prop)
    img_list_id = getattr(pref, prop_index)

    thumb_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                             'node_groups',
                             'thumb', sub_dir) + '/'
    if 'node_groups' not in img_list:
        item = img_list.add()
        setattr(pref, prop_index, len(img_list) - 1)
        item.name = 'node_groups'
        item.path = thumb_dir


def register():
    img_preview = previews.new(max_size=(512, 512))
    img_preview.img_dir = ""
    img_preview.img = ()
    __tempPreview__["adjt_thumbnails"] = img_preview

    bpy.utils.register_class(ViewAlignThumbProperty)
    bpy.utils.register_class(AnimateThumProperty)
    bpy.utils.register_class(T3DN_OT_bip_showcase_install_pillow)
    bpy.utils.register_class(ADJT_Preference)

    init_thumb('view_align_preset_list', 'view_align_preset_list_index', 'view align')
    init_thumb('anim_preset_list', 'anim_preset_list_index', 'animate')


def unregister():
    bpy.utils.unregister_class(ViewAlignThumbProperty)
    bpy.utils.unregister_class(AnimateThumProperty)
    bpy.utils.unregister_class(T3DN_OT_bip_showcase_install_pillow)
    bpy.utils.unregister_class(ADJT_Preference)

    clear_preview_cache()
