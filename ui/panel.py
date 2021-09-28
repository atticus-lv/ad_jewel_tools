import bpy
from .utils import check_unit

from .. import __folder_name__
from ..ops.utils import ADJT_NodeTree


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


preset = {'四视图_横向排布', '三视图_横向排布'}


class SidebarSetup:
    bl_category = "ADJT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DRAW_BOX'}


class ADJT_PT_UnitPanel(SidebarSetup, bpy.types.Panel):
    bl_label = ''

    bl_options = {'DRAW_BOX', 'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(self, context):
        return check_unit(context)

    def draw_header(self, context):
        layout = self.layout
        layout.alert = True
        layout.label(text='Scene scale is not optimal', icon='ERROR')

    def draw(self, context):
        layout = self.layout
        layout.alert = True

        layout.scale_y = 1.25
        row = layout.row(align=1)
        row.operator('wm.adjt_set_units', icon='DRIVER_DISTANCE')


class ADJT_PT_CurvePanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Curve and Flow'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Curve', icon='OUTLINER_OB_CURVE')
        box.operator('adjt.extract_edge_as_curve', icon='CURVE_NCURVE')
        box.operator('adjt.offset_curve_by_length', icon='DRIVER_DISTANCE')

        box = layout.box()
        box.label(text='Flow', icon='CURVE_DATA')
        box.operator('adjt.flow_mesh_along_curve', icon='FORCE_CURVE')
        box.operator('adjt.split_curve_and_flow_mesh', icon='GP_MULTIFRAME_EDITING')


class ADJT_PT_AlignPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Geo Tools'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Instance', icon='LIGHTPROBE_GRID')
        box.operator("node.adjt_join_geo")

        box = layout.box()
        box.label(text='Align', icon='MOD_ARRAY')

        # select the instance will not show the preset thumbnails
        if not (context.active_object and context.active_object.name.startswith('ADJT_Render')):
            pref = get_pref()
            item = pref.view_align_preset_list[pref.view_align_preset_list_index]
            if item:
                col = box.column(align=1)
                col.template_icon_view(item, "thumbnails", scale=5, scale_popup=8, show_labels=False)
                p = item.thumbnails[:-4]

                col.label(text=p)
                box.operator('node.adjt_view_align', icon='IMPORT', text='Align').node_group_name = p
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


class ADJT_PT_UtilityPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Utility'
    bl_options = {'DRAW_BOX','DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.operator('wm.adjt_batch_rename',icon = 'FONT_DATA')
        box.operator('adjt.init_thumb')
        row = box.row(align=True)
        row.label(text='Load Files', icon='FILEBROWSER')
        pref = get_pref()
        row.prop(pref,'load_ui',toggle = True)
        row = box.row(align=True)
        row.operator('wm.adjt_load_file', icon='BACK', text='Previous').action = '-1'
        row.operator('wm.adjt_load_file', icon='FORWARD', text='Next').action = '+1'
        # box.label(text='Measure', icon='CON_DISTLIMIT')
        #
        # if not (hasattr(context.active_object, 'adjt_measure') and context.active_object.type == 'FONT'):
        #     box.operator('adjt.measure_bind', icon='OUTLINER_OB_FONT').update_object = ''
        #
        # else:
        #     box2 = box.box().column()
        #     box2.label(text='Font Settings', icon='OUTLINER_OB_FONT')
        #     box2.operator('adjt.measure_bind', text='Update Font',
        #                   icon='FILE_REFRESH').update_object = context.active_object.name
        #     box2.prop(context.active_object.data, 'space_character', text='Space')
        #
        #     box2.prop(context.active_object.data, 'offset_x')
        #     box2.prop(context.active_object.data, 'offset_y')


class ADJT_PT_AnimatePanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Animate'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Animate', icon='MOD_ARRAY')

        # select the instance will not show the preset thumbnails
        if not (context.active_object and context.active_object.name.startswith('ADJT_Animate')):
            pref = get_pref()
            item = pref.anim_preset_list[pref.anim_preset_list_index]
            if item:
                col = box.column(align=1)
                col.template_icon_view(item, "thumbnails", scale=5, scale_popup=8, show_labels=False)
                p = item.thumbnails[:-4]

                col.label(text=p)
                box.operator('node.adjt_view_align', icon='IMPORT', text='Animate').node_group_name = p
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
                if node is not None and 'Object' in node.inputs:
                    box2.label(text='Settings', icon='OBJECT_DATA')
                    obj = node.inputs['Object'].default_value
                    box2.operator('adjt.set_active_object', icon='RESTRICT_SELECT_OFF',
                                  text='Select Source').obj_name = obj.name

                    for input in node.inputs:
                        box2.prop(input, 'default_value', text=input.name)


class ADJT_PT_RenderPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Render'
    bl_options = {'DRAW_BOX','DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Camera', icon='SCENE')
        box.operator('render.adjt_cam_frame', icon='IMAGE_PLANE')

        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object
            if cam.data.type == 'ORTHO':
                box3 = box.box()
                box3.label(text='Camera', icon='CAMERA_DATA')
                box3.prop(cam.data, 'ortho_scale')

        #####################
        box = layout.box()
        row = box.row(align=True)
        row.label(text='Lighting', icon='WORLD')
        row.operator("preferences.studiolight_show", text="", icon="PREFERENCES")

        view = context.space_data
        shading = view.shading if view.type == 'VIEW_3D' else context.scene.display.shading

        if shading.type != 'RENDERED':
            box.operator('render.adjt_init_shading')
        else:
            col = box.column()
            row = col.row(align=True)
            row.prop(context.scene, 'adjt_world_mode', expand=True)
            if context.scene.adjt_world_mode == 'PREVIEW':
                col.template_icon_view(shading, "studio_light", scale_popup=3, scale=5)
                col.prop(shading, "studiolight_rotate_z", text="Rotation")
                col.prop(shading, "studiolight_intensity")
                col.operator("adjt.apply_world", icon='IMPORT')
            else:
                if not context.scene.world:
                    col.label(text='No context world!')
                else:
                    world_nt = ADJT_NodeTree(context.scene.world.node_tree)
                    node_background = world_nt.get_node("SSM_BG")
                    node_hsv = world_nt.get_node("SSM_HSV")
                    node_rotate_x = world_nt.get_node("SSM_Rv_x")
                    node_rotate_y = world_nt.get_node("SSM_Rv_y")
                    node_rotate_z = world_nt.get_node("SSM_Rv")

                    col = col.box().column()

                    col.separator(factor=0.5)

                    col.prop(context.scene.render, 'film_transparent', toggle=1)

                    if node_background:
                        input = node_background.inputs[1]
                        col.prop(input, 'default_value', text=input.name)

                    col.separator(factor=0.5)

                    if node_rotate_x:
                        input = node_rotate_x.outputs[0]
                        col.prop(input, 'default_value', text='X')

                    if node_rotate_y:
                        input = node_rotate_y.outputs[0]
                        col.prop(input, 'default_value', text='Y')

                    if node_rotate_z:
                        input = node_rotate_z.outputs[0]
                        col.prop(input, 'default_value', text='Z')

                    col.separator(factor=0.5)

                    if node_hsv:
                        for input in node_hsv.inputs:
                            if input.is_linked: continue
                            col.prop(input, 'default_value', text=input.name)


def register():
    bpy.utils.register_class(ADJT_PT_UnitPanel)
    bpy.utils.register_class(ADJT_PT_CurvePanel)
    bpy.utils.register_class(ADJT_PT_AlignPanel)
    bpy.utils.register_class(ADJT_PT_UtilityPanel)
    # bpy.utils.register_class(ADJT_PT_AnimatePanel)
    bpy.utils.register_class(ADJT_PT_RenderPanel)


def unregister():
    bpy.utils.unregister_class(ADJT_PT_UnitPanel)
    bpy.utils.unregister_class(ADJT_PT_CurvePanel)
    bpy.utils.unregister_class(ADJT_PT_AlignPanel)
    bpy.utils.unregister_class(ADJT_PT_UtilityPanel)
    # bpy.utils.unregister_class(ADJT_PT_AnimatePanel)
    bpy.utils.unregister_class(ADJT_PT_RenderPanel)
