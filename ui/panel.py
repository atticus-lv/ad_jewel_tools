import bpy
from .utils import check_unit

from .. import __folder_name__


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


preset = {'四视图_横向排布', '三视图_横向排布'}


class SidebarSetup:
    bl_category = "ADJT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


class ADJT_PT_SidePanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'AD Jewel Tools'

    def draw(self, context):
        layout = self.layout

        set = check_unit(context)
        if set:
            box = layout.box()
            box.alert = True
            box.label(text='Scene scale is not optimal', icon='ERROR')
            box.operator('adjt.set_units', icon='DRIVER_DISTANCE')

        box = layout.box()
        box.label(text='Curve', icon='OUTLINER_OB_CURVE')
        box.operator('adjt.extract_edge_as_curve', icon='CURVE_NCURVE')
        box.operator('adjt.offset_curve_by_length', icon='DRIVER_DISTANCE')

        box = layout.box()
        box.label(text='Flow', icon='CURVE_DATA')
        box.operator('adjt.flow_mesh_along_curve', icon='FORCE_CURVE')
        box.operator('adjt.split_curve_and_flow_mesh', icon='GP_MULTIFRAME_EDITING')

        box = layout.box()
        box.label(text='Align', icon='MOD_ARRAY')

        # select the instance will not show the preset thumbnails
        if not (context.active_object and context.active_object.name.startswith('ADJT_Render')):
            pref = get_pref()
            item = pref.view_align_preset_list[pref.view_align_preset_list_index]
            if item:
                box.template_icon_view(item, "thumbnails", scale=8, show_labels=True)
                p = item.thumbnails[:-4]
                box.operator('adjt.view_align', icon='IMPORT', text='Align').node_group_name = p
        else:
            mod = None
            for m in context.active_object.modifiers:
                if m.type == 'NODES':
                    mod = m
                    break
            if mod:
                nt = mod.node_group
                node = nt.nodes.get('Group')
                box2 = box.box()
                if node is not None and 'Separate' in node.inputs:
                    box2.label(text='Instance Settings', icon='OBJECT_DATA')
                    obj = node.inputs['Object'].default_value
                    box2.operator('adjt.set_active_object', icon='RESTRICT_SELECT_OFF',
                                  text='Select Source').obj_name = obj.name

                    for input in node.inputs:
                        box2.prop(input, 'default_value', text=input.name)

        box = layout.box()
        box.label(text='Render', icon='SCENE')
        box.operator('adjt.cam_frame', icon='IMAGE_PLANE')

        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object
            if cam.data.type == 'ORTHO':
                box3 = box.box()
                box3.label(text='Camera', icon='CAMERA_DATA')
                box3.prop(cam.data, 'ortho_scale')


def register():
    bpy.utils.register_class(ADJT_PT_SidePanel)


def unregister():
    bpy.utils.unregister_class(ADJT_PT_SidePanel)
