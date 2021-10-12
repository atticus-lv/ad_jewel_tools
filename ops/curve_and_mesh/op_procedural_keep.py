import bpy
import bmesh

from ...ops.utils import ADJT_NodeTree


class ADJT_OT_ProceduralKeep(bpy.types.Operator):
    """Procedural Delete in Edit mode"""
    bl_idname = 'mesh.adjt_procedural_keep'
    bl_label = 'Procedural Keep'
    bl_options = {'UNDO_GROUPED'}

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT'

    def execute(self, context):
        ob = context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        # select invert
        verts = [i for i, v in enumerate(bm.verts) if v.select is False]

        # add vertex group
        bpy.ops.object.mode_set(mode='OBJECT')
        vg = ob.vertex_groups.new(name="Selected Invert")
        vg.add(verts, 1.0, 'ADD')

        # mode modifier
        nt = bpy.data.node_groups.new(name='Procedural Keep', type='GeometryNodeTree')
        self.create_delete_node_tree(nt, vg.name)

        mod = ob.modifiers.new(name='Procedural Keep', type='NODES')
        mod.node_group = nt
        mod.show_on_cage = True

        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        context.view_layer.objects.active = ob

        return {'FINISHED'}

    def create_delete_node_tree(self, node_tree, group_name):
        nt = ADJT_NodeTree(node_tree)
        node_delete = nt.add_node('GeometryNodeLegacyDeleteGeometry')
        node_delete.inputs[1].default_value = group_name
        node_delete.location = (0, 0)

        node_input = nt.add_node('NodeGroupInput')
        node_input.location = (-300, 0)
        nt.link_node(node_input.outputs[0], node_delete.inputs[0])

        node_output = nt.add_node('NodeGroupOutput')
        node_output.location = (300, 0)
        nt.link_node(node_delete.outputs[0], node_output.inputs[-1])


def register():
    bpy.utils.register_class(ADJT_OT_ProceduralKeep)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ProceduralKeep)
