import bpy
from bpy.props import StringProperty, EnumProperty
from .utils import check_unit

from .. import __folder_name__
from ..ops.utils import ADJT_NodeTree
from ..ui.icon_utils import BatchPreview

bat_preview = BatchPreview('.bip')


def get_pref():
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__folder_name__).preferences


def has_adjt_modifier(obj, prefix='ADJT'):
    for mod in obj.modifiers:
        if mod.name.startswith(prefix): return True


class SidebarSetup:
    bl_category = "ADJT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(self, context):
        return get_pref().use_workflow_panel is False

    def draw(self, context):
        layout = self.layout
        self.draw_ui(context, layout)

    def draw_ui(self, context, layout):
        pass


class ADJT_PT_UnitPanel(SidebarSetup, bpy.types.Panel):
    bl_label = ''

    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(self, context):
        return check_unit(context)

    def draw_header(self, context):
        layout = self.layout
        layout.alert = True
        layout.label(text='Scene scale is not optimal', icon='ERROR')

    def draw_ui(self, context, layout):
        layout.scale_y = 1.25
        row = layout.row(align=1)
        row.alignment = 'CENTER'
        row.separator()
        row.operator('wm.adjt_set_units', icon_value=bat_preview.get_icon('set_unit'))


class ADJT_PT_CurvePanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Model'

    def draw_ui(self, context, layout):
        box = layout.box()
        box.label(text='Mesh & Curve', icon_value=bat_preview.get_icon('extract_curve'))
        box.operator('mesh.adjt_extract_edge_as_curve', icon_value=bat_preview.get_icon('extract_curve'))
        box.operator('curve.adjt_offset_curve_by_length', icon_value=bat_preview.get_icon('offset_curve'))
        box.operator('curve.adjt_flow_mesh_along_curve', icon_value=bat_preview.get_icon('flow'))
        box.operator('curve.adjt_split_curve_and_flow_mesh', icon_value=bat_preview.get_icon('split'))

        box = layout.box()
        box.label(text='Procedural Tools', icon_value=bat_preview.get_icon('place'))
        row = box.row(align=False)
        row.alignment = 'CENTER'
        row.scale_y = 1.5
        row.scale_x = 1.5
        row.operator("mesh.adjt_procedural_translate", icon_value=bat_preview.get_icon('transform'), text='')
        row.operator("mesh.adjt_procedural_rotate", icon_value=bat_preview.get_icon('rotate'), text='')
        row.operator("mesh.adjt_procedural_scale", icon_value=bat_preview.get_icon('scale'), text='')
        box.operator("mesh.adjt_center_origin", icon_value=bat_preview.get_icon('origin'))

        box.operator("node.adjt_join_geo", icon_value=bat_preview.get_icon('join'))
        box.operator("mesh.adjt_realize_instance", icon_value=bat_preview.get_icon('instance'))
        box.operator("node.adjt_apply_instance", icon_value=bat_preview.get_icon('apply'))
        box.operator("node.transfer_attribute", icon_value=bat_preview.get_icon('transfer'))
        box.operator('mesh.adjt_procedural_keep', icon_value=bat_preview.get_icon('delete'))

        box = layout.box()
        box.label(text='Procedural Preset', icon_value=bat_preview.get_icon('nodes'))

        mesh_curve = box.operator('node.adjt_curve', text='General MS', icon_value=bat_preview.get_icon('curve'))
        mesh_curve.version = '1.0'
        mesh_curve.node_group_name = 'General MS'

        mesh_curve = box.operator('node.adjt_curve', text='General Custom Curve',
                                  icon_value=bat_preview.get_icon('curve'))
        mesh_curve.version = '1.0'
        mesh_curve.node_group_name = 'General Custom Curve'

        circle = box.operator('node.adjt_array', icon_value=bat_preview.get_icon('circulay_array'),
                              text='Circular Array')
        circle.node_group_name = 'Circular Array'
        circle.version = '1.1'

        grid = box.operator('node.adjt_array', icon_value=bat_preview.get_icon('grid_array'),
                            text='Grid Array')
        grid.node_group_name = 'Grid Array'
        grid.version = '1.1'

        box.operator('node.curve_scatter', icon_value=bat_preview.get_icon('flow'))


class ADJT_PT_AlignPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Align'

    def draw_ui(self, context, layout):
        box = layout.box()
        box.label(text='Align', icon_value=bat_preview.get_icon('align2'))

        # select the instance will not show the preset thumbnails
        if context.active_object is not None and hasattr(context.active_object, 'modifiers'):
            pref = get_pref()
            item = pref.view_align_preset_list[pref.view_align_preset_list_index]
            if item:
                col = box.column(align=1)
                col.template_icon_view(item, "thumbnails", scale=5, scale_popup=5, show_labels=False)
                p = item.thumbnails[:-4]

                col.label(text=p)
                b = box.operator('node.adjt_view_align', text='Align')
                b.node_group_name = p
                b.version = 'v1'
                b.modifier_name = 'ADJT_ViewAlign'
                b.dir_name = 'node_groups'
                b.file_name = 'view_align_preset.blend'


class ADJT_PT_MeasurePanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Measure'

    def draw_ui(self, context, layout):
        box = layout.box().column()
        pref = get_pref()
        box.label(text='Weighting', icon_value=bat_preview.get_icon('weight2'))

        box_list = box.row(align=True)
        box_list.template_list(
            "ADJT_UL_WeightList", "Weight List",
            pref, "weight_list",
            pref, "weight_list_index")

        box_btn = box_list.column(align=True)
        box_btn.operator('adjt.weight_list_add', icon='ADD', text='')
        box_btn.operator('adjt.weight_list_remove', icon='REMOVE', text='')
        box_btn.separator()
        box_btn.operator('adjt.weight_list_move_up', icon='TRIA_UP', text='')
        box_btn.operator('adjt.weight_list_move_down', icon='TRIA_DOWN', text='')
        box_btn.separator()
        # box_btn.operator('adjt.weight_list_copy',icon = 'DUPLICATE', text='')
        if len(pref.weight_list) > 0:
            item = pref.weight_list[pref.weight_list_index]
            box.prop(item, 'composition', text='', icon='INFO')

        box.separator(factor=0.5)
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.scale_y = 1.5
        row.scale_x = 1.25
        row.separator()
        row.operator('mesh.adjt_check_weight')

        box = layout.box()
        box.label(text='Measure', icon_value=bat_preview.get_icon('measure'))

        box.operator('adjt.measure_bind', )

        box = layout.box()
        box.label(text='Font', icon_value=bat_preview.get_icon('rename'))
        box.operator('mesh.adjt_set_font')


class ADJT_PT_UtilityPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Utility'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_ui(self, context, layout):
        box = layout.box()

        box.operator('ajdt.check_update', icon='INFO')

        box.operator('adjt.init_thumb', icon='BLENDER')

        box.operator('wm.call_menu_pie').name = 'ADJT_MT_pop_menu'

        box.operator('wm.adjt_batch_rename', icon='FONT_DATA')

        box = box.box()
        row = box.row(align=True)
        row.label(text='Load Files', icon='FILEBROWSER')
        pref = get_pref()
        row.prop(pref, 'load_ui', toggle=True)
        row = box.row(align=True)
        row.operator('wm.adjt_load_file', icon='BACK', text='Previous').action = '-1'
        row.operator('wm.adjt_load_file', icon='FORWARD', text='Next').action = '+1'


class ADJT_PT_AnimatePanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Animate'

    def draw_ui(self, context, layout):

        box = layout.box()
        box.label(text='Animate', icon_value=bat_preview.get_icon('animate'))

        # select the instance will not show the preset thumbnails
        if context.active_object is not None and hasattr(context.active_object, 'modifiers'):
            pref = get_pref()
            item = pref.anim_preset_list[pref.anim_preset_list_index]
            if item:
                col = box.column(align=1)
                col.template_icon_view(item, "thumbnails", scale=5, scale_popup=5, show_labels=False)
                p = item.thumbnails[:-4]

                col.label(text=p)
                box.operator('node.adjt_animate', text='Animate').node_group_name = p
        else:
            mod = None
            box.operator('screen.animation_play')
            if context.active_object is None: return
            for m in context.active_object.modifiers:
                if m.type == 'NODES' and m.name.startswith('ADJT_Animate'):
                    mod = m
                    break
            if mod:
                nt = mod.node_group
                node = nt.nodes.get('Group')
                box2 = box.box()
                if node is not None and 'FPS' in node.inputs:
                    box2.label(text='Settings', icon='OBJECT_DATA')

                    for input in node.inputs:
                        box2.prop(input, 'default_value', text=input.name)


class ADJT_PT_RenderPanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'Render'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_ui(self, context, layout):

        box = layout.box()
        box.label(text='Material', icon_value=bat_preview.get_icon('material'))
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.separator()
        row.template_ID_preview(
            context.window_manager, "adjt_tmp_mat",
            rows=3, cols=4, hide_buttons=True)
        box.operator('mesh.adjt_set_material')

        box = layout.box()
        box.label(text='Camera', icon_value=bat_preview.get_icon('frame'))
        box.operator('render.adjt_cam_frame')

        if context.active_object and context.active_object.type == 'CAMERA':
            cam = context.active_object
            if cam.data.type == 'ORTHO':
                box3 = box.box()
                box3.label(text='Camera', icon='CAMERA_DATA')
                box3.prop(cam.data, 'ortho_scale')

        #####################
        box = layout.box()
        row = box.row(align=True)
        row.label(text='Lighting', icon_value=bat_preview.get_icon('light'))
        row.operator("preferences.studiolight_show", text="", icon="PREFERENCES", emboss=False)

        view = context.space_data
        shading = view.shading if view.type == 'VIEW_3D' else context.scene.display.shading

        if shading.type != 'RENDERED':
            box.operator('render.adjt_init_shading')
        else:
            col = box.column()
            row = col.row(align=True)
            row.prop(context.scene, 'adjt_world_mode', expand=True)
            if context.scene.adjt_world_mode == 'PREVIEW':
                col.separator(factor=0.5)

                row = col.split(factor=0.5)
                row.template_icon_view(shading, "studio_light", scale_popup=3, scale=5)
                sub_col = row.column()
                sub_col.separator(factor=2)
                sub_col.prop(context.scene.render, 'film_transparent', toggle=1)
                sub_col.prop(shading, "studiolight_rotate_z", text="Rotation")
                sub_col.prop(shading, "studiolight_intensity")

                col.separator(factor=0.5)
                col.operator("adjt.apply_world", icon='IMPORT')

            else:
                if not context.scene.world:
                    col.label(text='No context world!')
                else:
                    world_nt = ADJT_NodeTree(context.scene.world.node_tree)
                    node_group = world_nt.get_node("adjt_quick_world_v1")

                    col = col.box().column()
                    col.separator(factor=0.5)
                    col.prop(context.scene.render, 'film_transparent', toggle=1)

                    if not node_group: return
                    if node_group.node_tree.name == 'adjt_quick_world_v1':
                        for input in node_group.inputs:
                            col.prop(input, 'default_value', text=input.name)


########

# icons = [
#     ('MODEL', 'Model', model_icon.get_image_icon_id()),
#     ('PLACE', 'Place', align_icon.get_image_icon_id()),
#     ('RENDER', 'Render', render_icon.get_image_icon_id()),
#     ('MEASURE', 'Measure', measure_icon.get_image_icon_id()),
#     ('TOOLS', 'Tools', tools_icon.get_image_icon_id()),
# ]


class ADJT_PT_Workflow(SidebarSetup, bpy.types.Panel):
    bl_label = ''

    bl_options = {"HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(self, context):
        return get_pref().use_workflow_panel is True

    def draw_header(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator('wm.adjt_load_file', icon='BACK', text='Load Pre').action = '-1'
        row.operator('wm.adjt_load_file', icon='FORWARD', text='Load Next').action = '+1'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=False)

        enum_icons = [

            ('MODEL', 'Model', '', 'place', 0),
            ('PLACE', 'Place', '', 'join', 1),
            ('RENDER', 'Render', '', 'render', 2),
            ('MEASURE', 'Measure', '', 'measure', 3),
            ('TOOLS', 'Tools', '', 'rename', 4),
        ]

        wm = context.window_manager
        curr = wm.adjt_workflow
        col = layout.column()

        row = col.row(align=False)
        row.prop(wm, 'adjt_workflow', expand=True)

        row = col.row(align=False)
        row.scale_y = 1.5
        row.scale_x = 1.1
        for e in enum_icons:
            if curr == e[0]:
                box = row.box()
                box.template_icon(bat_preview.get_icon(e[3]), scale=1.5)

            else:
                row.template_icon(bat_preview.get_icon(e[3] + '_dark'), scale=1.15)

        if wm.adjt_workflow == 'MODEL':
            ADJT_PT_CurvePanel.draw_ui(self, context, col)
        elif wm.adjt_workflow == 'PLACE':
            ADJT_PT_AlignPanel.draw_ui(self, context, col)
            ADJT_PT_AnimatePanel.draw_ui(self, context, col)
        elif wm.adjt_workflow == 'MEASURE':
            ADJT_PT_MeasurePanel.draw_ui(self, context, col)
        elif wm.adjt_workflow == 'TOOLS':
            ADJT_PT_UtilityPanel.draw_ui(self, context, col)
        elif wm.adjt_workflow == 'RENDER':
            ADJT_PT_RenderPanel.draw_ui(self, context, col)


def register():
    bat_preview.register()

    bpy.types.WindowManager.adjt_workflow = EnumProperty(name='Workflow', items=[
        ('MODEL', 'Model', ''),
        ('PLACE', 'Place', ''),
        ('RENDER', 'Render', ''),
        ('MEASURE', 'Measure', ''),
        ('TOOLS', 'Tools', ''),
    ])

    bpy.utils.register_class(ADJT_PT_UnitPanel)
    bpy.utils.register_class(ADJT_PT_Workflow)

    bpy.utils.register_class(ADJT_PT_CurvePanel)
    bpy.utils.register_class(ADJT_PT_AlignPanel)
    bpy.utils.register_class(ADJT_PT_UtilityPanel)
    bpy.utils.register_class(ADJT_PT_AnimatePanel)
    bpy.utils.register_class(ADJT_PT_RenderPanel)


def unregister():
    del bpy.types.WindowManager.adjt_workflow

    bpy.utils.unregister_class(ADJT_PT_UnitPanel)
    bpy.utils.register_class(ADJT_PT_Workflow)

    bpy.utils.unregister_class(ADJT_PT_Workflow)
    bpy.utils.unregister_class(ADJT_PT_CurvePanel)
    bpy.utils.unregister_class(ADJT_PT_AlignPanel)
    bpy.utils.unregister_class(ADJT_PT_UtilityPanel)
    bpy.utils.unregister_class(ADJT_PT_AnimatePanel)
    bpy.utils.unregister_class(ADJT_PT_RenderPanel)

    bat_preview.unregister()
