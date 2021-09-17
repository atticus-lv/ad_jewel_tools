import bpy
from .utils import check_unit


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
            box.label(text='场景不是最佳建模单位', icon='ERROR')
            box.operator('adjt.set_units', icon='DRIVER_DISTANCE')

        box = layout.box()
        box.label(text='Curve', icon='OUTLINER_OB_CURVE')
        box.operator('adjt.extract_edge_as_curve', icon='CURVE_NCURVE')
        box.operator('adjt.offset_curve_by_length', icon='DRIVER_DISTANCE')

        box = layout.box()
        box.label(text='Flow', icon='CURVE_DATA')
        box.operator('adjt.flow_mesh_on_curve', icon='FORCE_CURVE')
        box.operator('adjt.split_curve_and_flow_mesh', icon='GP_MULTIFRAME_EDITING')

        box = layout.box()
        box.label(text='Render', icon='SCENE')
        box.operator('adjt.view_align', icon='MOD_ARRAY')
        box.operator('adjt.cam_frame', icon='IMAGE_PLANE')


def register():
    bpy.utils.register_class(ADJT_PT_SidePanel)


def unregister():
    bpy.utils.unregister_class(ADJT_PT_SidePanel)
