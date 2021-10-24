import bpy
from bpy.props import StringProperty
from mathutils import Vector

from ..ops_utils.Template import ADJT_OT_ModalTemplate
from ..utils import ADJT_NodeTree

import random


class ADJT_OT_ApplyInstance(ADJT_OT_ModalTemplate):
    '''Apply geo data to new object
应用几何数据到新物体'''
    bl_label = "Apply Instance"
    bl_idname = "node.apply_instance"
    bl_options = {'UNDO_GROUPED'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Horizontal 4 View')

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and hasattr(context.active_object, 'modifiers')

    def main(self, context):
        # extra ob for display
        self.display_ob = self.create_obj()
        self.display_ob.name = f'{context.active_object.name}_Apply Instance'

        # mode modifier
        nt = bpy.data.node_groups.new(name='Apply Instance', type='GeometryNodeTree')
        mesh_count = self.create_join_geo_nodetree(nt, join_object=context.active_object)

        mod = self.display_ob.modifiers.new(name='Apply Instance', type='NODES')
        mod.node_group = nt

        bpy.ops.object.select_all(action='DESELECT')
        self.display_ob.select_set(True)
        context.view_layer.objects.active = self.display_ob
        # remove
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.node_groups.remove(nt)
        # tips
        self.tips.clear()
        self.tips.append(f'Apply {context.active_object.name}')

        self._finish = True

    def create_join_geo_nodetree(self, node_tree, join_object):
        nt = ADJT_NodeTree(node_tree)
        node_origin = nt.add_node('GeometryNodeObjectInfo', name='JOIN ORIGIN')
        node_origin.inputs[0].default_value = join_object  # origin to self, allow to move
        node_origin.location = (350, 320)
        node_origin.inputs[1].default_value = True

        node_realize = nt.add_node('GeometryNodeRealizeInstances')
        node_realize.location = (950, 0)
        nt.link_node(node_origin.outputs[3], node_realize.inputs[0])

        node_output = nt.add_node('NodeGroupOutput')
        node_output.location = (1150, 0)
        nt.link_node(node_realize.outputs[0], node_output.inputs[0])

    def create_obj(self):
        vertices = edges = faces = []
        new_mesh = bpy.data.meshes.new('adjt_empty_mesh')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        obj = bpy.data.objects.new('new_object', new_mesh)
        bpy.context.collection.objects.link(obj)

        return obj


def register():
    bpy.utils.register_class(ADJT_OT_ApplyInstance)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ApplyInstance)
