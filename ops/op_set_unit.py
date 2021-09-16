import bpy


class ADJT_OT_SetUnits(bpy.types.Operator):
    '''Set Units
设置场景单位为厘米'''
    bl_label = "设置场景单位"
    bl_idname = "adjt.set_units"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        unit = context.scene.unit_settings
        unit.system = "METRIC"
        unit.length_unit = "MILLIMETERS"
        unit.scale_length = 0.001
        context.space_data.overlay.grid_scale = 0.001

        self.report({"INFO"}, "已设置为场景单位毫米")

        return {"FINISHED"}

def register():
    bpy.utils.register_class(ADJT_OT_SetUnits)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_SetUnits)