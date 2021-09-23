import bpy


class ADJT_OT_SetActiveObject(bpy.types.Operator):
    bl_label = "Set Active Object"
    bl_idname = "adjt.set_active_object"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    obj_name: bpy.props.StringProperty(name='Object Name')

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj_name)
        if obj:
            obj.hide_set(False)
            obj.select_set(True)
            context.view_layer.objects.active = obj

        return {"FINISHED"}


def register():
    bpy.utils.register_class(ADJT_OT_SetActiveObject)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_SetActiveObject)
