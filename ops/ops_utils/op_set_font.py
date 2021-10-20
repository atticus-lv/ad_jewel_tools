import bpy
from bpy.props import StringProperty, EnumProperty
from ... import __folder_name__

import os


class ADJT_OT_FontSet(bpy.types.Operator):
    bl_label = "Set Font"
    bl_idname = "mesh.adjt_set_font"
    bl_options = {"REGISTER", "UNDO"}

    type: EnumProperty(name='Type', items=[
        ('NEW', 'New', ''),
        ('SET', 'Set', ''),
        ('APPEND', 'Append', ''),
        ('NEXT', 'Next', ''),
    ], default='NEW')

    text: StringProperty(name='Text', default='你爱写不写吧')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        row = layout.row(align=True)
        row.prop(self, 'type',expand=True)
        box = layout.column().box()
        box.prop(self, 'text')

    def create_font(self, context):
        font_curve = bpy.data.curves.new(type="FONT", name="Font Curve")
        font_curve.body = self.text
        font_obj = bpy.data.objects.new(name="Font Object", object_data=font_curve)
        context.collection.objects.link(font_obj)
        return font_obj

    def load_font(self):
        if 'Fontquan-XinYiJiXiangSong Regular' not in bpy.data.fonts:
            bpy.data.fonts.load(self.font_path)
        self.font = bpy.data.fonts.get('Fontquan-XinYiJiXiangSong Regular')
        print(self.font)
        return self.font

    def execute(self, context):
        self.load_font()
        if self.type == 'NEW':
            font_obj = self.create_font(context)
            font_obj.data.font = self.load_font()
            font_obj.data.body = self.text

        else:
            if context.object is None or context.active_object.type != 'FONT':
                self.report({"ERROR"}, 'Select Font object as active object')
                return {"CANCELLED"}

            font = context.active_object
            font.data.font = self.load_font()
            if self.type == 'SET':
                font.data.body = self.text
            elif self.type == 'APPEND':
                font.data.body += self.text
            elif self.type == 'NEXT':
                font.data.body += f'\n{self.text}'

        return {"FINISHED"}

    def invoke(self, context, event):
        self.font_path = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                      'fonts', 'ZiTiQuanXinYiJiXiangSong-2.ttf')

        return context.window_manager.invoke_props_dialog(self, width=400)


def register():
    bpy.utils.register_class(ADJT_OT_FontSet)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_FontSet)
