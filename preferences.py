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
from . import __folder_name__


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


# Image items
####################

__tempPreview__ = {}  # store in global, delete in unregister

image_extensions = ('.png', '.jpg', '.jpeg')


def check_extension(input_string: str, extensions: set) -> bool:
    for ex in extensions:
        if input_string.endswith(ex): return True


def clear_preview_cache():
    for preview in __tempPreview__.values():
        previews.remove(preview)
    __tempPreview__.clear()


def enum_thumbnails_from_dir_items(self, context):
    pref = get_pref()
    enum_items = []
    if context is None: return enum_items

    try:
        item = pref.view_align_preset_list[pref.view_align_preset_list_index]
        directory = item.path
    except(Exception):
        directory = ""

    # store
    image_preview = __tempPreview__["adjt_thumbnails"]

    if directory == image_preview.img_dir:
        return image_preview.img

    if directory and os.path.exists(directory):
        image_paths = []
        for fn in os.listdir(directory):
            if check_extension(fn.lower(), image_extensions):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
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


def update_path_name2(self, context):
    full_dir_name = os.path.dirname(self.path) if os.path.isdir(self.path) else None
    if full_dir_name is None: return None
    self.name = full_dir_name.replace('\\', '/').split('/')[-1]


class ImageDirListItemProperty(PropertyGroup):
    name: StringProperty(name='name')
    path: StringProperty(name='dir', description='folder dir', subtype='DIR_PATH', update=update_path_name2)
    thumbnails: EnumProperty(name='thumb', items=enum_thumbnails_from_dir_items)


from .ui.t3dn_bip.ops import InstallPillow


class T3DN_OT_bip_showcase_install_pillow(bpy.types.Operator, InstallPillow):
    bl_idname = 't3dn.bip_showcase_install_pillow'


# Preference
####################


class ADJT_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    view_align_preset_list: CollectionProperty(type=ImageDirListItemProperty)
    view_align_preset_list_index: IntProperty(default=0, min=0, name='Active')

    anim_preset_list:CollectionProperty(type=ImageDirListItemProperty)
    anim_preset_list_index: IntProperty(default=0, min=0, name='Active')


    def draw(self, context):
        layout = self.layout
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
    img_preview = previews.new()
    img_preview.img_dir = ""
    img_preview.img = ()
    __tempPreview__["adjt_thumbnails"] = img_preview

    bpy.utils.register_class(ImageDirListItemProperty)
    bpy.utils.register_class(T3DN_OT_bip_showcase_install_pillow)
    bpy.utils.register_class(ADJT_Preference)

    init_thumb('view_align_preset_list','view_align_preset_list_index','view align')
    init_thumb('anim_preset_list','anim_preset_list_index','animate')


def unregister():
    bpy.utils.unregister_class(ImageDirListItemProperty)
    bpy.utils.unregister_class(T3DN_OT_bip_showcase_install_pillow)
    bpy.utils.unregister_class(ADJT_Preference)

    clear_preview_cache()
