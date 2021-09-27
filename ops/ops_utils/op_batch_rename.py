import bpy
from bpy.props import StringProperty, EnumProperty


class ADJT_OT_BatchRename(bpy.types.Operator):
    bl_label = "Batch Rename"
    bl_idname = "adjt.batch_rename"
    bl_options = {"REGISTER", "UNDO"}

    type: EnumProperty(name='Type', items=[
        ('SET', 'Set', ''),
        ('CASE', 'Case', ''),
    ], default='SET')

    case_method: EnumProperty(name='Method', items=[
        ('UPPER', 'Upper Case', ''),
        ('LOWER', 'Lower Case', ''),
        ('TITLE', 'Title Case', ''),
    ], default='TITLE')

    set_name: StringProperty(name='Name')
    set_method: EnumProperty(name='Method', items=[
        ('NEW', 'New', ''),
        ('PREFIX', 'Prefix', ''),
        ('SUFFIX', 'Suffix', ''),
    ], default='NEW')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, 'type')
        box = layout.column().box()
        if self.type == 'SET':
            row = box.row(align=1)
            row.prop(self, 'set_method', expand=True)
            box.prop(self, 'set_name')
        else:
            row = box.row(align=1)
            row.prop(self, 'case_method', expand=True)

        layout.label(text=f'Rename {len(context.selected_objects)} Objects')

    def execute(self, context):
        for obj in context.selected_objects:
            if self.type == "SET":
                if self.set_method == 'NEW':
                    obj.name = self.set_name
                elif self.set_method == 'PREFIX':
                    obj.name = self.set_name + obj.name
                else:
                    obj.name += self.set_name
            elif self.type == 'CASE':
                if self.case_method == 'UPPER':
                    obj.name = obj.name.upper()
                elif self.case_method == 'LOWER':
                    obj.name = obj.name.lower()
                else:
                    obj.name = obj.name.title()

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self,width=400)


def register():
    bpy.utils.register_class(ADJT_OT_BatchRename)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_BatchRename)
