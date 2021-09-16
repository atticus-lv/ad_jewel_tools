import bpy


class ADJT_OT_ExtractEdgeAsCurve(bpy.types.Operator):
    bl_idname = 'adjt.extract_edge_as_curve'
    bl_label = 'Extract Edge As Curve'

    def poll(self):
        if bpy.context.active_object is not None:
            return bpy.cotext.active_object.mode == 'EDIT' and bpy.cotext.active_object.type == 'MESH'

    def execute(self, context):
        # copy
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode": 1},
                                    TRANSFORM_OT_translate={"value": (0, 0, 0), "orient_type": 'GLOBAL',
                                                            "orient_matrix": ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
                                                            "orient_matrix_type": 'GLOBAL',
                                                            "constraint_axis": (False, False, False), "mirror": False,
                                                            "use_proportional_edit": False,
                                                            "proportional_edit_falloff": 'SMOOTH',
                                                            "proportional_size": 1,
                                                            "use_proportional_connected": False,
                                                            "use_proportional_projected": False, "snap": False,
                                                            "snap_target": 'CLOSEST', "snap_point": (0, 0, 0),
                                                            "snap_align": False, "snap_normal": (0, 0, 0),
                                                            "gpencil_strokes": False, "cursor_transform": False,
                                                            "texture_space": False, "remove_on_cancel": False,
                                                            "release_confirm": False, "use_accurate": False,
                                                            "use_automerge_and_split": False})
        # separate
        bpy.ops.mesh.separate(type='SELECTED')

        bpy.ops.object.mode_set(mode='OBJECT')

        # exclude the select object
        a = None
        for obj in bpy.context.selected_objects:
            if obj != bpy.context.active_object:
                a = obj
                break
        bpy.context.view_layer.objects.active = a
        bpy.ops.object.convert(target='CURVE')
        # restore
        bpy.ops.object.select_all(action='DESELECT')
        a.select_set(True)

        return {'FINISHED'}

def  register():
    bpy.util.register_class(ADJT_OT_ExtractEdgeAsCurve)

def  unregister():
    bpy.util.unregister_class(ADJT_OT_ExtractEdgeAsCurve)