import bpy
import bmesh

from bpy.props import StringProperty, PointerProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup

from ..ops_utils.op_template import ADJT_OT_ModalTemplate
from ..utils import get_dep_coll
from mathutils import Vector


# some code from Measurelt tools
def get_smart_selected(obj, context):
    index_list = []
    loc_list = []
    # if not mesh, no vertex
    if obj.type != "MESH":
        return index_list
    # --------------------
    # meshes
    # --------------------
    oldobj = context.object
    context.view_layer.objects.active = obj
    flag = False

    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        flag = True

    bm = bmesh.from_edit_mesh(obj.data)
    for v in bm.verts:
        if not v.select: continue
        loc_list.append(v.co)

    if flag is True:
        bpy.ops.object.editmode_toggle()
    # Back context object
    context.view_layer.objects.active = oldobj

    return index_list, loc_list


class ADJT_OT_MeasureBind(ADJT_OT_ModalTemplate):
    '''Generate Measure text from selected points
从选中点生成测量字体'''
    bl_label = "Create Measure Font"
    bl_idname = "adjt.measure_bind"
    bl_options = {'REGISTER', 'UNDO'}

    update_object: StringProperty()

    @classmethod
    def poll(self, context):
        o = context.active_object
        if o is None:
            return False
        else:
            if o.type == "MESH":
                if context.mode == 'EDIT_MESH':
                    return True
                else:
                    return False

            elif o.type == 'FONT' and self.update_object != '':
                return True
            else:
                return False

    def main(self, context):
        if self.update_object != '':
            obj = bpy.data.objects.get(self.update_object)
            update_bind_target(obj.adjt_measure, context)
            self.title = f'Update {self.update_object}'
        else:
            index, pos = get_smart_selected(context.active_object, context)

            if len(pos) > 1:
                dep_coll = get_dep_coll('Measure Dep', context)

                target1 = self.create_empty_obj(pos[0], link_coll=dep_coll)
                target2 = self.create_empty_obj(pos[1], link_coll=dep_coll)

                font = self.create_obj(link_coll=dep_coll)
                font.adjt_measure.use = True

                font.adjt_measure.target1 = target1
                font.adjt_measure.target2 = target2

        self._finish = True

    def create_empty_obj(self, point: Vector, link_coll=None):
        obj = bpy.data.objects.new("Empty", None)
        obj.location = point
        if not link_coll:
            bpy.context.collection.objects.link(obj)
        else:
            link_coll.objects.link(obj)

        return obj

    def create_obj(self, link_coll=None):
        font_curve = bpy.data.curves.new(type="FONT", name="Font Curve")
        font_curve.body = "ADJT Example"
        font_obj = bpy.data.objects.new(name="Font Object", object_data=font_curve)

        if not link_coll:
            bpy.context.collection.objects.link(font_obj)
        else:
            link_coll.objects.link(font_obj)

        return font_obj


metric_dict = {
    'KILOMETERS': 'km',
    'METERS': 'm',
    'CENTIMETERS': 'cm',
    'MILLIMETERS': 'mm',
    'MICROMETERS': 'um',
}


def update_bind_target(self, context):
    object = self.id_data
    if not self.use: return
    if 'target1' in object.constraints:
        cons = object.constraints.get('target1')
    else:
        cons = object.constraints.new(type='COPY_LOCATION')
        cons.name = 'target1'

    cons.influence = 1
    if self.target1:
        cons.target = self.target1
        self.target1.empty_display_type = 'SPHERE'

    if 'target2' in object.constraints:
        cons2 = object.constraints.get('target2')
    else:
        cons2 = object.constraints.new(type='COPY_LOCATION')
        cons2.name = 'target2'

    cons2.influence = 0.5
    if self.target2:
        cons2.target = self.target2
        self.target2.empty_display_type = 'SPHERE'

    # move to top
    while object.constraints[0] != cons:
        bpy.ops.constraint.move_up(constraint=cons.name, owner=self)

    if self.target1 and self.target2:
        len = (self.target1.location - self.target2.location).length
        object.data.body = str(round(len, 3))
        object.location = (self.target1.location + self.target2.location) / 2
        if bpy.context.scene.unit_settings.system == 'METRIC':
            unit = bpy.context.scene.unit_settings.length_unit
            postfix = metric_dict[unit]
            object.data.body += postfix

        object.data.align_x = 'CENTER'
        object.data.align_y = 'CENTER'
        object.data.size = len * 0.1
        self.target1.empty_display_size = len * 0.05
        self.target2.empty_display_size = len * 0.05


class TextMeasureBindProperty(PropertyGroup):
    use: BoolProperty(default=False)
    target1: PointerProperty(type=bpy.types.Object, update=update_bind_target)
    target2: PointerProperty(type=bpy.types.Object, update=update_bind_target)


def poll_font(self, object):
    return object.type == 'FONT'


def register():
    bpy.utils.register_class(TextMeasureBindProperty)
    bpy.types.Object.adjt_measure = PointerProperty(type=TextMeasureBindProperty, poll=poll_font)
    bpy.utils.register_class(ADJT_OT_MeasureBind)


def unregister():
    bpy.utils.unregister_class(TextMeasureBindProperty)
    del bpy.types.Text.adjt_measure
    bpy.utils.unregister_class(ADJT_OT_MeasureBind)
