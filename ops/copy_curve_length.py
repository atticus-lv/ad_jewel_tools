import bpy


def est_curve_length(ob: Object) -> float:
    if ob.modifiers:

        # Reset curve
        # ---------------------------

        settings = {
            "bevel_object": None,
            "bevel_depth": 0.0,
            "extrude": 0.0,
        }

        for k, v in settings.items():
            x = getattr(ob.data, k)
            setattr(ob.data, k, v)
            settings[k] = x

        # Calculate length
        # ---------------------------

        depsgraph = bpy.context.evaluated_depsgraph_get()
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh()
        me.transform(ob.matrix_world)

        bm = bmesh.new()
        bm.from_mesh(me)

        ob_eval.to_mesh_clear()

        length = 0.0

        for edge in bm.edges:
            length += edge.calc_length()

        bm.free()

        # Restore curve
        # ---------------------------

        for k, v in settings.items():
            setattr(ob.data, k, v)

    else:

        curve = ob.data.copy()
        curve.transform(ob.matrix_world)

        length = 0.0

        for spline in curve.splines:
            length += spline.calc_length()

        bpy.data.curves.remove(curve)

    return length
