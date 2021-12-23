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


def enum_jewel_icon(self, context):
    pref = get_pref()
    return enum_thumbnails_from_dir_items(pref.weight_list, pref.weight_list_index, context)


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


class WeightProperty(PropertyGroup):
    thumbnails: EnumProperty(name='thumb', items=[('COLOR_01', '01', '', 'SEQUENCE_COLOR_01', 1),
                                                  ('COLOR_02', '02', '', 'SEQUENCE_COLOR_02', 2),
                                                  ('COLOR_03', '03', '', 'SEQUENCE_COLOR_03', 3),
                                                  ('COLOR_04', '04', '', 'SEQUENCE_COLOR_04', 4),
                                                  ('COLOR_05', '05', '', 'SEQUENCE_COLOR_05', 5),
                                                  ('COLOR_06', '06', '', 'SEQUENCE_COLOR_06', 6),
                                                  ('COLOR_07', '07', '', 'SEQUENCE_COLOR_07', 7),
                                                  ('COLOR_08', '08', '', 'SEQUENCE_COLOR_08', 8)])

    name: StringProperty(name='Name')
    composition: StringProperty(name='Composition')
    density: FloatProperty(name='cm³/g', min=0, soft_max=20)
    use: BoolProperty(name='Use', default=True)


from .ui.t3dn_bip.ops import InstallPillow


class T3DN_OT_bip_showcase_install_pillow(bpy.types.Operator, InstallPillow):
    bl_idname = 't3dn.bip_showcase_install_pillow'


# Preference
####################

import rna_keymap_ui


class ADJT_Preference(bpy.types.AddonPreferences):
    bl_idname = __package__

    # tools
    load_ui: BoolProperty(name='Load UI')

    # preset
    view_align_preset_list: CollectionProperty(type=ViewAlignThumbProperty)
    view_align_preset_list_index: IntProperty(default=0, min=0, name='Active')

    anim_preset_list: CollectionProperty(type=AnimateThumProperty)
    anim_preset_list_index: IntProperty(default=0, min=0, name='Active')

    weight_list: CollectionProperty(type=WeightProperty)
    weight_list_index: IntProperty(default=0, min=0, name='Active')
    # ui
    use_workflow_panel: BoolProperty(name='Use Workflow Panel', default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'use_workflow_panel')
        # layout.operator('t3dn.bip_showcase_install_pillow', text='安装Pillow（加快预览加载）')
        self.drawKeymap()

    def drawKeymap(self):
        col = self.layout.box().column()
        # col.label(text="Keymap", icon="KEYINGSET")
        km = None
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        old_km_name = ""
        get_kmi_l = []

        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname and kmi_add.name == kmi_con.name:
                    get_kmi_l.append((km, kmi_con))

        get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

        for km, kmi in get_kmi_l:
            if not km.name == old_km_name:
                col.label(text=str(km.name), icon="DOT")

            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

            old_km_name = km.name


addon_keymaps = []

from .ui.panel import ADJT_PT_UtilityPanel, ADJT_PT_AnimatePanel, ADJT_PT_AlignPanel, ADJT_PT_CurvePanel
from .ui.panel import ADJT_PT_MeasurePanel, ADJT_PT_RenderPanel


class ADJT_MT_pop_menu(bpy.types.Menu):
    bl_label = "ADJT"
    bl_idname = "ADJT_MT_pop_menu"

    @classmethod
    def poll(self, context):
        return context.area.ui_type == 'VIEW_3D'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        col = pie.column(align=True)
        ADJT_PT_AlignPanel.draw_ui(self, context, col)
        col.separator()
        ADJT_PT_RenderPanel.draw_ui(self, context, col)
        col = pie.column(align=True)
        ADJT_PT_CurvePanel.draw_ui(self, context, col)

        pie.separator()

        pie.popover(panel='ADJT_PT_MeasurePanel')



def add_keybind():
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'A', 'PRESS', ctrl=True, shift=True)
        kmi.properties.name = "ADJT_MT_pop_menu"
        addon_keymaps.append((km, kmi))


def remove_keybind():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()


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

    bpy.utils.register_class(WeightProperty)
    bpy.utils.register_class(ViewAlignThumbProperty)
    bpy.utils.register_class(AnimateThumProperty)
    bpy.utils.register_class(T3DN_OT_bip_showcase_install_pillow)
    bpy.utils.register_class(ADJT_Preference)
    bpy.utils.register_class(ADJT_MT_pop_menu)

    init_thumb('view_align_preset_list', 'view_align_preset_list_index', 'view align')
    init_thumb('anim_preset_list', 'anim_preset_list_index', 'animate')

    # add_keybind()


def unregister():
    bpy.utils.unregister_class(WeightProperty)
    bpy.utils.unregister_class(ViewAlignThumbProperty)
    bpy.utils.unregister_class(AnimateThumProperty)
    bpy.utils.unregister_class(T3DN_OT_bip_showcase_install_pillow)
    bpy.utils.unregister_class(ADJT_Preference)
    bpy.utils.unregister_class(ADJT_MT_pop_menu)

    clear_preview_cache()

    # remove_keybind()
