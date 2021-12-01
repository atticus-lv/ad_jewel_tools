import bpy
from bpy.props import StringProperty
from mathutils import Vector

from ..ops_utils.Template import ADJT_OT_ModalTemplate
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
            return len(context.selected_objects) > 0 and hasattr(context.active_object, 'modifiers')

    def main(self, context):
        # extra ob for display
        self.display_ob = self.create_obj()
        self.display_ob.name = f'{context.active_object.name} Join'

        # mode modifier
        nt = bpy.data.node_groups.new(name=f'{context.active_object.name} Join', type='GeometryNodeTree')
        mesh_count = self.create_join_geo_nodetree(nt, context.selected_objects, join_object=self.display_ob)

        mod = self.display_ob.modifiers.new(name='Join Geo', type='NODES')
        mod.node_group = nt

        bpy.ops.object.select_all(action='DESELECT')
        self.display_ob.select_set(True)
        context.view_layer.objects.active = self.display_ob

        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Join {mesh_count} mesh objects to ')

        self._finish = True

    def create_join_geo_nodetree(self, node_tree, selected_objects, join_object):
        nt = ADJT_NodeTree(node_tree)
        node_join_all = nt.add_node('GeometryNodeJoinGeometry')
        node_join_all.location = (350, 0)

        # expose view
        ########
        node_set_position = nt.add_node('GeometryNodeSetPosition')
        node_set_position.location = (550, 0)

        node_vector_math = nt.add_node('ShaderNodeVectorMath')
        node_vector_math.operation = 'MULTIPLY'
        node_vector_math.location = (350, -200)

        node_position = nt.add_node('GeometryNodeInputPosition')
        node_position.location = (150, -200)
        node_value = nt.add_node('ShaderNodeValue')
        node_value.outputs[0].default_value = 1
        node_value.location = (150, -350)

        nt.link_node(node_join_all.outputs[0], node_set_position.inputs[0])
        nt.link_node(node_vector_math.outputs[0], node_set_position.inputs[2])

        nt.link_node(node_position.outputs[0], node_vector_math.inputs[0])
        nt.link_node(node_value.outputs[0], node_vector_math.inputs[1])
        ########

        node_origin = nt.add_node('GeometryNodeObjectInfo', name='JOIN ORIGIN')
        node_origin.inputs[0].default_value = join_object  # origin to self, allow to move
        node_origin.location = (350, 320)

        node_mesh_line = nt.add_node('GeometryNodeMeshLine')
        node_mesh_line.inputs[0].default_value = 1  # set only one point
        node_mesh_line.location = (550, 320)

        node_instance_on_points = nt.add_node('GeometryNodeInstanceOnPoints')
        node_instance_on_points.location = (750, 50)

        nt.link_node(node_origin.outputs[0], node_mesh_line.inputs[2])
        nt.link_node(node_mesh_line.outputs[0], node_instance_on_points.inputs[0])
        nt.link_node(node_set_position.outputs[0], node_instance_on_points.inputs['Instance'])

        # node_realize = nt.add_node('GeometryNodeRealizeInstances')
        # node_realize.location = (950, 0)
        # nt.link_node(node_instance_on_points.outputs[0], node_realize.inputs[0])

        node_input = nt.add_node('NodeGroupInput')
        node_input.location = (0,0)

        node_output = nt.add_node('NodeGroupOutput')
        node_output.location = (1150, 0)
        nt.link_node(node_instance_on_points.outputs[0], node_output.inputs[-1])

        coll_dict = {}

        for obj in selected_objects:
            if not hasattr(obj, 'modifiers'): continue

            if obj.type == 'CURVE':
                if obj.data.dimensions != '3D': continue

                if len(obj.modifiers) == 0:
                    if obj.data.bevel_mode in {'ROUND', 'PROFILE'}:
                        if obj.data.bevel_depth == 0: continue

                    elif obj.data.bevel_mode == 'OBJECT':
                        if obj.data.bevel_object is None: continue

                    elif obj.data.offset == 0 and obj.data.extrude == 0:
                        continue

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

            node_switch= nt.add_node('GeometryNodeSwitch', name=f'Switch {coll}')
            node_switch.location = Vector((150, frame.location[1] + 250))

            nt.link_node(node_input.outputs[-1], node_switch.inputs[1])
            node_switch.inputs[1].default_value = True
            nt.nt.inputs[-1].name = f'{coll}'

            nt.link_node(node_join.outputs[-1], node_switch.inputs[14])
            nt.link_node(node_switch.outputs[6], node_join_all.inputs[0])

            for obj in items:
                col_count += 1
                mesh_count += 1

                node_obj = nt.add_node('GeometryNodeObjectInfo', name=obj.name)
                node_obj.transform_space = 'RELATIVE'
                node_obj.label = obj.name
                node_obj.inputs[1].default_value = True # set instance

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
