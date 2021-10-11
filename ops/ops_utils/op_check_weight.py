# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import bmesh

from ..ops_utils.op_template import ADJT_OT_ModalTemplate

import os
from bpy.props import EnumProperty, IntProperty, FloatProperty


def clean_float(value: float, precision: int = 0) -> str:
    # Avoid scientific notation and strip trailing zeros: 0.000 -> 0.0

    text = f"{value:.{precision}f}"
    index = text.rfind(".")

    if index != -1:
        index += 2
        head, tail = text[:index], text[index:]
        tail = tail.rstrip("0")
        text = head + tail

    return text


def get_unit(unit_system: str, unit: str) -> tuple[float, str]:
    # Returns unit length relative to meter and unit symbol

    units = {
        "METRIC": {
            "KILOMETERS": (1000.0, "km"),
            "METERS": (1.0, "m"),
            "CENTIMETERS": (0.01, "cm"),
            "MILLIMETERS": (0.001, "mm"),
            "MICROMETERS": (0.000001, "µm"),
        },
        "IMPERIAL": {
            "MILES": (1609.344, "mi"),
            "FEET": (0.3048, "\'"),
            "INCHES": (0.0254, "\""),
            "THOU": (0.0000254, "thou"),
        },
    }

    try:
        return units[unit_system][unit]
    except KeyError:
        fallback_unit = "CENTIMETERS" if unit_system == "METRIC" else "INCHES"
        return units[unit_system][fallback_unit]


def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=False):
    """Returns a transformed, triangulated copy of the mesh"""

    assert obj.type == 'MESH'

    if apply_modifiers and obj.modifiers:
        import bpy
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        me = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        obj_eval.to_mesh_clear()
    else:
        me = obj.data
        if obj.mode == 'EDIT':
            bm_orig = bmesh.from_edit_mesh(me)
            bm = bm_orig.copy()
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

    # TODO. remove all customdata layers.
    # would save ram

    if transform:
        bm.transform(obj.matrix_world)

    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm


class ADJT_OT_CheckWeight(bpy.types.Operator):
    bl_label = "Check Weight"
    bl_idname = "mesh.adjt_check_weight"
    bl_options = {"UNDO", "INTERNAL"}

    # data
    obj = None

    check_type: EnumProperty(name='Check Type', items=[
        ('VOLUME', 'Volume', ''),
        ('AREA', 'Area', ''),
    ])

    area_thickness: FloatProperty(name='Thickness', default=0.13)

    mat_list = [(19.32, 'Yellow Gold 24K', 'Au 99.9%'),
                (10.36, 'Silver Sterling', 'Ag 92.5%, Cu 7.5%'),
                (0.9, 'Wax', ''), ]

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, 'check_type')
        if self.check_type == 'AREA':
            layout.prop(self, 'area_thickness')

    def invoke(self, context, event):
        self.obj = context.active_object
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        bm = bmesh_copy_from_object(obj=self.obj, apply_modifiers=True)
        volume = 0

        if self.check_type == 'VOLUME':
            volume = bm.calc_volume()
        elif self.check_type == 'AREA':
            area = sum(f.calc_area() for f in bm.faces)
            volume = area * self.area_thickness

        scene = context.scene
        unit = scene.unit_settings
        scale = 1.0 if unit.system == 'NONE' else unit.scale_length

        if unit.system == 'NONE':
            volume_fmt = clean_float(volume, 8)
            volume_str = 'No Unit Set'
        else:
            length, symbol = get_unit(unit.system, unit.length_unit)

            volume_unit = volume * (scale ** 3.0) / (length ** 3.0)
            volume_str = clean_float(volume_unit, 4)
            volume_fmt = f"{volume_str} {symbol}"

        mat_list = self.mat_list

        def draw_ans(self, context):
            layout = self.layout

            layout.operator('adjt.clip_board', text=f"{volume_fmt}³").data = str(volume_fmt)
            layout.separator()
            for mat in mat_list:
                data = str(round(mat[0] * eval(volume_str) / 1000, 2))
                layout.operator('adjt.clip_board', text=f'{mat[1]}: {data}g').data = data

        context.window_manager.popup_menu(draw_func=draw_ans, title='Result', icon='INFO')

        return {"FINISHED"}


def register():
    bpy.utils.register_class(ADJT_OT_CheckWeight)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_CheckWeight)
