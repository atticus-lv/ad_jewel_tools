import bpy


class ADJT_OT_operator(bpy.types.Operator):
    """Separate active curve object by loose parts"""
    bl_idname = "adjt.split_curve"
    bl_label = "split curve by loose parts"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'CURVE'

    def execute(self, context):
        # remove selection
        bpy.ops.object.select_all(action='DESELECT')

        origin = context.active_object
        origin.select_set(1)

        splines = origin.data.splines
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.curve.select_all(action='DESELECT')

        while len(splines) > 1:
            spline = splines[0]
            if spline.bezier_points:
                spline.bezier_points[0].select_control_point = True
            elif spline.points:
                spline.points[0].select = True
            bpy.ops.curve.select_linked()
            bpy.ops.curve.separate()

        print(context.selected_objects)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ADJT_OT_operator)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_operator)


if __name__ == "__main__":
    register()
