import bpy
from ..ops_utils.op_template import ADJT_OT_ModalTemplate

# some code from jewelcraft
# https://github.com/mrachinskiy/jewelcraft
class ADJT_OT_SetUnits(ADJT_OT_ModalTemplate):
    '''Set Units
设置场景单位为厘米'''
    bl_label = "Set Units (mm)"
    bl_idname = "adjt.set_units"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    tips = ['',
            'Scene Unit has been set to mm']

    def main(self, context):
        unit = context.scene.unit_settings
        unit.system = "METRIC"
        unit.length_unit = "MILLIMETERS"
        unit.scale_length = 0.001
        context.space_data.overlay.grid_scale = 0.001

        self.report({"INFO"}, "Scene Unit has been set to mm")

        self._finish = True

def register():
    bpy.utils.register_class(ADJT_OT_SetUnits)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_SetUnits)