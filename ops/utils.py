import bpy
import bmesh


def copy_obj(obj, link_data=False):
    new_obj = obj.copy()
    if not link_data: new_obj.data = obj.data.copy()
    bpy.context.collection.objects.link(new_obj)
    return new_obj


def get_dep_coll(name, context):
    if name not in context.scene.collection.children:
        dep_coll_dir = bpy.data.collections.new(name)
        context.scene.collection.children.link(dep_coll_dir)
    else:
        dep_coll_dir = context.scene.collection.children[name]

    return dep_coll_dir


def est_curve_length(ob) -> float:
    # some code from jewelcraft
    # https://github.com/mrachinskiy/jewelcraft
    if ob.modifiers:

        # Reset curve_and_mesh
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

        # Restore curve_and_mesh
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


# node tools

class ADJT_NodeTree:
    def __init__(self, node_tree, cache_links=None):
        self.nt = node_tree
        self.nodes = self.nt.nodes
        self.cache_links = cache_links

    def get_node(self, name):
        return self.nodes.get(name)

    def add_node(self, type, name=None):
        node = self.nodes.new(type)
        if name:
            node.name = name
        return node

    def remove_node(self, name):
        node = self.get_node(name)
        if node: self.nodes.remove(node)

    def link_node(self, output, input):
        if input.is_linked is False:
            return self.nt.links.new(output, input)
        else:
            return self.nt.links.new(output, input) if input.links[0].to_socket != output else input.links[0]


# Draw Tools
import blf
import gpu
import bgl

from math import cos, sin, pi, hypot

from gpu_extras.batch import batch_for_shader
from mathutils import Vector


def dpifac():
    prefs = bpy.context.preferences.system
    return prefs.dpi * prefs.pixel_size / 72


def draw_pre(width=1):
    bgl.glLineWidth(width)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    bgl.glHint(bgl.GL_LINE_SMOOTH_HINT, bgl.GL_NICEST)


def draw_post():
    # restore
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)


def draw_tri_fan(shader, vertices, color):
    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def draw_line(x1, y1, x2, y2, size, color=(1.0, 1.0, 1.0, 0.7)):
    shader = gpu.shader.from_builtin('2D_SMOOTH_COLOR')

    vertices = ((x1, y1), (x2, y2))
    vertex_colors = ((color[0] + (1.0 - color[0]) / 4,
                      color[1] + (1.0 - color[1]) / 4,
                      color[2] + (1.0 - color[2]) / 4,
                      color[3] + (1.0 - color[3]) / 4),
                     color)

    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices, "color": vertex_colors})
    bgl.glLineWidth(size * dpifac())

    shader.bind()
    batch.draw(shader)


def get_real_location(obj, pos: Vector):
    return obj.matrix_world @ Vector(pos)


def draw_line_3d(start_pos, end_pos, color=(1.0, 1.0, 1.0, 0.7)):
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": [start_pos, end_pos]})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def draw_nurbs_curve(obj, color=(1.0, 1.0, 1.0, 0.7)):
    for spline in obj.data.splines:
        if spline.use_cyclic_u:
            draw_line_3d(get_real_location(obj, spline.points[0].co[:-1]),
                         get_real_location(obj, spline.points[-1].co[:-1]), color)

        for i, point in enumerate(spline.points):
            if i == 0: continue
            draw_line_3d(get_real_location(obj, point.co[:-1]),
                         get_real_location(obj, spline.points[i - 1].co[:-1]), color)


def draw_circle_2d_filled(shader, mx, my, radius, color=(1.0, 1.0, 1.0, 0.7)):
    radius = radius * dpifac()
    sides = 12
    vertices = [(radius * cos(i * 2 * pi / sides) + mx,
                 radius * sin(i * 2 * pi / sides) + my)
                for i in range(sides + 1)]

    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def draw_round_rectangle(shader, points, radius=8, color=(1.0, 1.0, 1.0, 0.7)):
    """points index top_right  top_left bottom_left bottom_right """

    sides = 16
    radius = 16

    # fill
    draw_tri_fan(shader, points, color)

    top_left = points[1]
    top_right = points[0]
    bottom_left = points[2]
    bottom_right = points[3]

    # Top edge
    top_left_top = (top_left[0], top_left[1] + radius)
    top_right_top = (top_right[0], top_right[1] + radius)
    vertices = [top_right_top, top_left_top, top_left, top_right]
    draw_tri_fan(shader, vertices, color)

    # Left edge
    top_left_left = (top_left[0] - radius, top_left[1])
    bottom_left_left = (bottom_left[0] - radius, bottom_left[1])
    vertices = [top_left, top_left_left, bottom_left_left, bottom_left]
    draw_tri_fan(shader, vertices, color)

    # Bottom edge
    bottom_left_bottom = (bottom_left[0], bottom_left[1] - radius)
    bottom_right_bottom = (bottom_right[0], bottom_right[1] - radius)
    vertices = [bottom_right, bottom_left, bottom_left_bottom, bottom_right_bottom]
    draw_tri_fan(shader, vertices, color)

    # right edge
    top_right_right = (top_right[0] + radius, top_right[1])
    bottom_right_right = (bottom_right[0] + radius, bottom_right[1])
    vertices = [top_right_right, top_right, bottom_right, bottom_right_right]
    draw_tri_fan(shader, vertices, color)

    # Top right corner
    vertices = [top_right]
    mx = top_right[0]
    my = top_right[1]
    for i in range(sides + 1):
        if 0 <= i <= 4:
            cosine = radius * cos(i * 2 * pi / sides) + mx
            sine = radius * sin(i * 2 * pi / sides) + my
            vertices.append((cosine, sine))

    draw_tri_fan(shader, vertices, color)

    # Top left corner
    vertices = [top_left]
    mx = top_left[0]
    my = top_left[1]
    for i in range(sides + 1):
        if 4 <= i <= 8:
            cosine = radius * cos(i * 2 * pi / sides) + mx
            sine = radius * sin(i * 2 * pi / sides) + my
            vertices.append((cosine, sine))

    draw_tri_fan(shader, vertices, color)

    # Bottom left corner
    vertices = [bottom_left]
    mx = bottom_left[0]
    my = bottom_left[1]
    for i in range(sides + 1):
        if 8 <= i <= 12:
            cosine = radius * cos(i * 2 * pi / sides) + mx
            sine = radius * sin(i * 2 * pi / sides) + my
            vertices.append((cosine, sine))

    draw_tri_fan(shader, vertices, color)

    # Bottom right corner
    vertices = [bottom_right]
    mx = bottom_right[0]
    my = bottom_right[1]
    for i in range(sides + 1):
        if 12 <= i <= 16:
            cosine = radius * cos(i * 2 * pi / sides) + mx
            sine = radius * sin(i * 2 * pi / sides) + my
            vertices.append((cosine, sine))

    draw_tri_fan(shader, vertices, color)


class DrawMsgHelper():
    def __init__(self, font_id, color3, alpha):
        self.font_id = font_id
        self.color = color3
        self.alpha = alpha
        blf.color(font_id, self.color[0], self.color[1], self.color[2], self.alpha)

        self.width, self.height = self.get_region_size()

    def set_alpha(self, alpha):
        self.alpha = alpha
        blf.color = (self.font_id, self.color[0], self.color[1], self.color[2], self.alpha)

    def get_text_length(self, text):
        return blf.dimensions(self.font_id, text)[0]

    def get_text_height(self, text):
        return blf.dimensions(self.font_id, text)[1]

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


class DrawHandle:
    def __init__(self, context, operator, View3D=False):
        self.operator = operator
        if View3D:
            self.handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback, (self.operator, context),
                'WINDOW', 'POST_VIEW')
        else:
            self.handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback, (self.operator, context),
                'WINDOW', 'POST_PIXEL')

    def draw_callback(self, context):
        # custom method overwrite
        pass

    def remove_handle(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
