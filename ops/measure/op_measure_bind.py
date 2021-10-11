import bpy
import bmesh

from bpy.props import StringProperty, PointerProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup

from ..ops_utils.op_template import ADJT_OT_ModalTemplate
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


class ADJT_OT_MeasureBind(ADJT_OT_ModalTemplate):
    '''Generate Measure text from selected points
从选中点生成测量字体'''
    bl_label = "Create Measure Font"
    bl_idname = "adjt.measure_bind"
    bl_options = {'UNDO'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Measure')

    def main(self, context):
        self.display_ob = self.create_obj()
        self.display_ob.name = 'ADJT_Measure'
        mod = self.display_ob.modifiers.new(name='Measure', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)

        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Apply "{self.node_group_name}" preset')
        self._finish = True

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'measure_preset.blend')

        node_group_dir = os.path.join(base_dir, 'NodeTree') + '/'

        if node_group_name in bpy.data.node_groups:
            preset_node = bpy.data.node_groups[node_group_name]
        else:
            bpy.ops.wm.append(filename=node_group_name, directory=node_group_dir)
            preset_node = bpy.data.node_groups[node_group_name]

        return preset_node

    def create_obj(self):
        vertices = edges = faces = []
        new_mesh = bpy.data.meshes.new('adjt_empty_mesh')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        obj = bpy.data.objects.new('new_object', new_mesh)
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
