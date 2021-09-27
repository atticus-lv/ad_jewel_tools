import bpy


class ADJT_OT_BatchRename(bpy.types.Operator):
    bl_label = "Batch Rename"
    bl_idname = "adjt.batch_rename"
    bl_options = {"REGISTER", "UNDO"}

    new_name: bpy.props.StringProperty(name='Object Name')

    def execute(self, context):
        for obj in  context.selected_objects:
            obj.name = self.new_name
        return {"FINISHED"}

    def  invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)


def register():
    bpy.utils.register_class(ADJT_OT_BatchRename)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_BatchRename)
