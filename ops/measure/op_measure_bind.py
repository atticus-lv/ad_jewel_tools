import bpy
import bmesh

from bpy.props import StringProperty, PointerProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup

from ..ops_utils.Template import ADJT_OT_ModalTemplate
from ... import __folder_name__
import os


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


class ADJT_OT_MeasureBind(bpy.types.Operator):
    '''Generate Measure text from selected points
从选中点生成测量字体'''
    bl_label = "Create Measure Font"
    bl_idname = "adjt.measure_bind"
    bl_options = {'UNDO'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Measure 1.0')

    def execute(self, context):
        # enable vertex color
        if context.preferences.experimental.use_sculpt_vertex_colors is False:
            context.preferences.experimental.use_sculpt_vertex_colors = True

        self.display_ob = self.create_obj(name='ADJT_Measure')
        mod = self.display_ob.modifiers.new(name='ADJT_Measure', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)

        # parent object for moving
        obj1 = self.create_empty(name='Pos1')
        obj2 = self.create_empty(name='Pos2')
        mod["Input_2"] = obj1
        mod["Input_3"] = obj2
        mod["Output_11_attribute_name"] = 'ADJT_Measure_color'

        # set empty
        obj1.parent = obj2.parent = self.display_ob
        obj1.empty_display_type = 'SPHERE'
        obj2.empty_display_type = 'SPHERE'

        obj1.location = (5, 0, 0)
        obj2.location = (-5, 0, 0)

        obj1.lock_scale[0] = obj2.lock_scale[0] = True
        obj1.lock_scale[1] = obj2.lock_scale[1] = True
        obj1.lock_scale[2] = obj2.lock_scale[2] = True

        obj1.show_in_front = obj2.show_in_front = True

        self.display_ob.select_set(False)
        obj1.select_set(True)
        obj2.select_set(True)

        return {"FINISHED"}

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'measure_preset.blend')

        with bpy.data.libraries.load(base_dir, link=False) as (data_from, data_to):
            data_to.node_groups = [name for name in data_from.node_groups if name == node_group_name]

        preset_node = data_to.node_groups[0]

        return preset_node

    def create_empty(self, name=''):
        obj = bpy.data.objects.new(name, None)
        bpy.context.collection.objects.link(obj)
        return obj

    def create_obj(self, name='new_object'):
        vertices = edges = faces = []
        new_mesh = bpy.data.meshes.new('adjt_empty_mesh')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        obj = bpy.data.objects.new(name, new_mesh)
        bpy.context.collection.objects.link(obj)

        return obj


metric_dict = {
    'KILOMETERS': 'km',
    'METERS': 'm',
    'CENTIMETERS': 'cm',
    'MILLIMETERS': 'mm',
    'MICROMETERS': 'um',
}


def register():
    bpy.utils.register_class(ADJT_OT_MeasureBind)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_MeasureBind)
