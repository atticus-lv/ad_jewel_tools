import bpy
import blf, bgl, gpu


def copy_obj(obj, link_data=False):
    new_obj = obj.copy()
    if not link_data: new_obj.data = obj.data.copy()
    bpy.context.collection.objects.link(new_obj)
    return new_obj


def est_curve_length(ob) -> float:
    # some code from jewelcraft
    # https://github.com/mrachinskiy/jewelcraft
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


class DrawHelper():
    def __init__(self, font_id, color3, alpha):
        self.font_id = font_id
        self.color = color3
        self.alpha = alpha
        blf.color(font_id, self.color[0], self.color[1], self.color[2], self.alpha)

        self.width, self.height = self.get_region_size()

    def set_alpha(self, alpha):
        self.alpha = alpha
        blf.color = (self.font_id, self.color[0], self.color[1], self.color[2], self.alpha)

    def get_text_length(self, text, height=False):
        return blf.dimensions(self.font_id, text)[0] if not height else blf.dimensions(self.font_id, text)[1]

    def draw_title(self, size=50, x=0, y=0, text="test title", align_center_x=True):
        # if align_center_x:
        #     dim_x = blf.dimensions(self.font_id, text)[0] / 2
        #     blf.position(self.font_id, self.width / 2 - dim_x, y, 0)
        # else:
        blf.position(self.font_id, x, y, 0)

        blf.size(self.font_id, size, 72)
        blf.draw(self.font_id, text)

    def draw_info(self, size=25, x=0, y=0, text="test info", align_center_x=True):
        # if align_center_x:
        #     dim_x = blf.dimensions(self.font_id, text)[0] / 2
        #     blf.position(self.font_id, self.width / 2 - dim_x, y, 0)
        # else:
        blf.position(self.font_id, x, y, 0)

        blf.size(self.font_id, size, 72)
        blf.draw(self.font_id, text)

    @staticmethod
    def get_region_size(muti_x=1, muti_y=1):
        width = bpy.context.region.width
        height = bpy.context.region.height
        return width * muti_x, height * muti_y
