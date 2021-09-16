import bpy
from .utils import check_unit

class SidebarSetup:
    bl_category = "ADJT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


class ADJT_PT_SidePanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'AD珠宝小工具'

    def draw(self, context):
        layout = self.layout
        set = check_unit(context)
        if set:
            box = layout.box()
            box.label(text='场景不是最佳建模单位')
            box.operator('adjt.set_units')

        layout.operator('adjt.extract_edge_as_curve')
        layout.operator('adjt.flow_mesh_on_curve')
        layout.operator('adjt.offset_curve_by_length')
        layout.operator('adjt.split_curve_and_flow_mesh')

        pass

def register():
    bpy.utils.register_class(ADJT_PT_SidePanel)


def unregister():
    bpy.utils.unregister_class(ADJT_PT_SidePanel)