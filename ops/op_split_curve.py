import bpy


class ADJT_OT_SplitCurveAndFlowMesh(bpy.types.Operator):
    """First select mesh then add select curve
先选网格物体再加选曲线曲线"""
    bl_idname = "adjt.split_curve_and_flow_mesh"
    bl_label = "split curve and flow mesh 分离流动曲线网格"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'CURVE' and len(context.selected_objects) == 2

    def execute(self, context):
        ori_curve = context.active_object
        ori_mesh = [obj for obj in context.selected_objects if obj != ori_curve][0]
        bpy.ops.object.select_all(action='DESELECT')

        ori_curve.select_set(1)

        # start split
        #############
        splines = ori_curve.data.splines
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

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        #############
        # end split

        # copy and replace
        splits_curves = [obj for obj in context.selected_objects if obj != ori_curve]
        for new_curve in splits_curves:
            new_mesh = self.copy_obj(ori_mesh)
            self.replace_modifier_curve(new_mesh, ori_curve, new_curve)

        return {'FINISHED'}

    def copy_obj(self, obj):
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.animation_data_clear()
        bpy.context.collection.objects.link(new_obj)
        return new_obj

    def replace_modifier_curve(self, obj, src_curve, new_curve):
        for mod in obj.modifiers:
            # support array and curve modifier
            if mod.type not in {'CURVE', 'ARRAY'}: continue

            if mod.type == 'ARRAY':
                if mod.fit_type != 'FIT_CURVE': continue
                if mod.curve == src_curve: mod.curve = new_curve

            elif mod.type == 'CURVE':
                if mod.object == src_curve: mod.object = new_curve


def register():
    bpy.utils.register_class(ADJT_OT_SplitCurveAndFlowMesh)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_SplitCurveAndFlowMesh)


if __name__ == "__main__":
    register()
