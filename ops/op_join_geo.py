import bpy
import os
from bpy.props import StringProperty
from .. import __folder_name__

from .op_utils import ADJT_OT_ModalTemplate
from .utils import ADJT_NodeTree


class ADJT_OT_JoinGeo(ADJT_OT_ModalTemplate):
    '''Copy the select obj to align view
选择并复制当前物体为三视图'''
    bl_label = "Join With Geo Nodes"
    bl_idname = "adjt.join_geo"
    bl_options = {'REGISTER', 'UNDO'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Horizontal 4 View')

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) > 0 and context.active_object.type == 'MESH'

    def main(self, context):
        nt = bpy.data.node_groups.new(name='Join Geo', type='GeometryNodeTree')
        mesh_count = self.create_join_geo_nodetree(nt, context.selected_objects)

        # extra ob for display
        self.display_ob = self.create_obj()

        self.display_ob.name = 'Join Geo'
        mod = self.display_ob.modifiers.new(name='Join Geo', type='NODES')
        mod.node_group = nt

        if 'Join Geo Dep' not in context.scene.collection.children:
            dep_coll_dir = bpy.data.collections.new("Join Geo Dep")
            context.scene.collection.children.link(dep_coll_dir)
        else:
            dep_coll_dir = context.scene.collection.children['Join Geo Dep']

        context.collection.objects.unlink(self.display_ob)
        dep_coll_dir.objects.link(self.display_ob)
        context.view_layer.objects.active = self.display_ob

        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Join {mesh_count} mesh objects to ')

        self._finish = True

    def create_join_geo_nodetree(self, node_tree, selected_objects):
        nt = ADJT_NodeTree(node_tree)
        node_join = nt.add_node('GeometryNodeJoinGeometry')
        node_join.location = (0, -100)

        node_output = nt.add_node('NodeGroupOutput')
        node_output.location = (200, -100)
        nt.link_node(node_join.outputs[0], node_output.inputs[-1])

        mesh_count = 0
        line_count = 10

        for obj in selected_objects:
            if obj.type != 'MESH': continue
            mesh_count += 1

            node_obj = nt.add_node('GeometryNodeObjectInfo', name=obj.name)
            node_obj.transform_space = 'RELATIVE'
            node_obj.label = obj.name

            node_obj.location = ((mesh_count % line_count + 1) * -250,
                                 -200 * (line_count - mesh_count // line_count - 1))

            node_obj.inputs[0].default_value = obj
            nt.link_node(node_obj.outputs[-1], node_join.inputs[0])

        return mesh_count

    def create_obj(self):
        vertices = edges = faces = []
        new_mesh = bpy.data.meshes.new('adjt_empty_mesh')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        obj = bpy.data.objects.new('new_object', new_mesh)
        bpy.context.collection.objects.link(obj)

        return obj


def register():
    bpy.utils.register_class(ADJT_OT_JoinGeo)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_JoinGeo)
