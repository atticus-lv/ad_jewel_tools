import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__
import bmesh

from ..ops_utils.op_template import ADJT_OT_ModalTemplate


class ProceduralTranform(bpy.types.Operator):
    """Procedural Delete in Edit mode"""
    bl_options = {'UNDO_GROUPED'}

    object = None
    display_ob = None
    node_group_name = 'Translate'

    default_z = 1.57

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type in {'MESH', 'CURVE', 'FONT'}

    def execute(self, context):
        self.display_ob = context.active_object

        # mode modifier
        mod = self.display_ob.modifiers.new(name='ADJT_ProceduralTransform', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)
        mod["Input_2"][2] = self.default_z
        # refresh
        mod.show_viewport = False
        mod.show_viewport = True

        return {'FINISHED'}

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'utils.blend')

        node_group_dir = os.path.join(base_dir, 'NodeTree') + '/'

        if node_group_name in bpy.data.node_groups:
            preset_node = bpy.data.node_groups[node_group_name]
        else:
            bpy.ops.wm.append(filename=node_group_name, directory=node_group_dir)
            preset_node = bpy.data.node_groups[node_group_name]

        # with bpy.data.libraries.load(base_dir, link=False) as (data_from, data_to):
        #     data_to.node_groups = [name for name in data_from.node_groups if name == node_group_name]
        #
        # preset_node = data_to.node_groups[0]

        return preset_node


class ADJT_OT_ProceduralTranslate(ProceduralTranform):
    bl_idname = 'mesh.adjt_procedural_translate'
    bl_label = 'Translate'

    node_group_name = 'Translate'


class ADJT_OT_ProceduralScale(ProceduralTranform):
    bl_idname = 'mesh.adjt_procedural_scale'
    bl_label = 'Scale'

    node_group_name = 'Scale'


class ADJT_OT_ProceduralRotate(ProceduralTranform):
    bl_idname = 'mesh.adjt_procedural_rotate'
    bl_label = 'Rotate'

    node_group_name = 'Rotate'


def register():
    bpy.utils.register_class(ADJT_OT_ProceduralTranslate)
    bpy.utils.register_class(ADJT_OT_ProceduralScale)
    bpy.utils.register_class(ADJT_OT_ProceduralRotate)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ProceduralTranslate)
    bpy.utils.unregister_class(ADJT_OT_ProceduralScale)
    bpy.utils.unregister_class(ADJT_OT_ProceduralRotate)