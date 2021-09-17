import bpy


def copy_obj(obj, link_data=False):
    new_obj = obj.copy()
    if not link_data: new_obj.data = obj.data.copy()
    bpy.context.collection.objects.link(new_obj)
    return new_obj


def est_curve_length(ob) -> float:
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


class ObjectHelper():
    def __init__(self, obj):
        self.obj = obj
        self.mx = obj.matrix_world

    def is_active(self):
        return self.obj == bpy.context.object

    def is_mesh(self):
        return self.obj.type == "MESH"

    def get_dimension(self):
        return self.obj.dimensions

    def get_max_bound(self) -> list:
        if self.is_mesh():
            return [
                max((self.mx @ v.co)[0] for v in self.obj.data.vertices),
                max((self.mx @ v.co)[1] for v in self.obj.data.vertices),
                max((self.mx @ v.co)[2] for v in self.obj.data.vertices),
            ]
        else:
            list(self.mx.translation)

    def get_min_bound(self) -> list:
        if self.is_mesh():
            return [
                max((self.mx @ v.co)[0] for v in self.obj.data.vertices),
                max((self.mx @ v.co)[1] for v in self.obj.data.vertices),
                max((self.mx @ v.co)[2] for v in self.obj.data.vertices),
            ]
        else:
            list(self.mx.translation)

    def get_mode(self):
        return self.obj.mode

    def add_vertex_color_layer(self, name: str):
        vcol_layer = self.obj.data.vertex_colors.new()
        vcol_layer.name = name
        return vcol_layer

    def remove_vertex_color_layer(self, name: str):
        if self.obj.data.vertex_colors:
            try:
                self.obj.data.vertex_colors.remove(self.obj.data.vertex_colors[name])
            except(Exception):
                pass

    def select_Ngon(self):
        mode = self.get_mode()
        self.obj.data.use_paint_mask = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)
        bpy.ops.object.mode_set(mode=mode)

    @staticmethod
    def get_PSR(obj):
        return obj.location, obj.scale, obj.rotation_euler

    @staticmethod
    def get_obj_maxz(obj) -> float:
        return max((obj.matrix_world @ v.co)[2] for v in obj.data.vertices) if obj.type == "MESH" else \
            obj.matrix_world.translation[2]

    @staticmethod
    def get_obj_minz(obj) -> float:
        return min((obj.matrix_world @ v.co)[2] for v in obj.data.vertices) if obj.type == "MESH" else \
            obj.matrix_world.translation[2]
