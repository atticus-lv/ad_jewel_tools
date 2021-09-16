import bpy


class SidebarSetup:
    bl_category = "ADJT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


class ADJT_PT_SidePanel(SidebarSetup, bpy.types.Panel):
    bl_label = 'AD珠宝小工具'

    def draw(self, context):
        layout = self.layout
        layout.operator('adjt.set_units')
        layout.operator('adjt.extract_edge_as_curve')
        layout.operator('adjt.split_curve_and_flow_mesh')
        pass
