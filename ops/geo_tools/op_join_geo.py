import bpy
from bpy.props import StringProperty
from mathutils import Vector

from ..ops_utils.op_template import ADJT_OT_ModalTemplate
from ..utils import ADJT_NodeTree

import random


class ADJT_OT_JoinGeo(ADJT_OT_ModalTemplate):
    '''Join geo data with geo node
使用几何节点合并几何数据'''
    bl_label = "Join Geometry"
    bl_idname = "node.adjt_join_geo"
    bl_options = {'UNDO_GROUPED'}

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

        context.view_layer.objects.active = self.display_ob
        self.display_ob.select_set(True)

        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Join {mesh_count} mesh objects to ')

        self._finish = True

    def create_join_geo_nodetree(self, node_tree, selected_objects):
        nt = ADJT_NodeTree(node_tree)
        node_join_all = nt.add_node('GeometryNodeJoinGeometry')
        node_join_all.location = (250, 0)

        node_output = nt.add_node('NodeGroupOutput')
        node_output.location = (500, 0)
        nt.link_node(node_join_all.outputs[0], node_output.inputs[-1])

        coll_dict = {}

        for obj in selected_objects:
            if obj.type not in {'CURVE', 'MESH'}: continue

            if obj.type == 'CURVE':
                if obj.data.dimensions != '3D': continue
                if obj.data.extrude == 0 or (
                        obj.data.bevel_mode in {'ROUND', 'PROFILE'} and obj.data.bevel_depth == 0) or (
                        obj.data.bevel_mode == 'OBJECT' and obj.data.bevel_object is None): continue

            if obj.users_collection[0].name not in coll_dict:
                coll_dict[obj.users_collection[0].name] = []

            coll_dict[obj.users_collection[0].name].append(obj)

        # count for row separate
        line_count = 0
        mesh_count = 0
        row_step = 250
        col_step = 250

        for coll, items in coll_dict.items():
            line_count += 1
            col_count = 0

            color = [round(random.random(), 1), round(random.random(), 1), round(random.random(), 1)]

            frame = nt.add_node('NodeFrame', name=f'Frame: {coll}')
            frame.label = coll
            frame.use_custom_color = True
            frame.color = color

            frame.location = (-1 * col_step * len(items), row_step * (line_count - 1))

            node_join = nt.add_node('GeometryNodeJoinGeometry', name=f'Join {coll}')
            node_join.location = Vector((0, frame.location[1] + 250))
            nt.link_node(node_join.outputs[-1], node_join_all.inputs[0])

            for obj in items:
                col_count += 1
                mesh_count += 1

                node_obj = nt.add_node('GeometryNodeObjectInfo', name=obj.name)
                node_obj.transform_space = 'RELATIVE'
                node_obj.label = obj.name

                node_obj.location = (col_count * -1 * col_step, line_count * row_step)

                node_obj.parent = frame

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
