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
from ...preferences import get_pref
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


class ADJT_UL_WeightList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=1)
        row.prop(item, 'thumbnails', text='',icon_only=True,emboss=False)
        row.prop(item, 'name', text='', emboss=False)
        row.prop(item, 'density', text='', emboss=False)
        row.prop(item, 'use', text='')


class ListAction:
    """Add / Remove / Copy current config"""
    bl_label = "Action List"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty()
    action = None

    def execute(self, context):
        pref = get_pref()

        if self.action == 'ADD':
            item = pref.weight_list.add()
            item.name = f'Weight{len(pref.weight_list)}'
            pref.weight_list_index = len(pref.weight_list) - 1

        elif self.action == 'REMOVE':
            pref.weight_list.remove(pref.weight_list_index)
            pref.weight_list_index = pref.weight_list_index - 1 if pref.weight_list_index != 0 else 0

        elif self.action == 'COPY':
            cur_item = pref.weight_list[self.index]

            item = pref.weight_list.add()
            item.name = cur_item.name + '_copy'
            item.use_config = cur_item.use_config
            item.extension = cur_item.extension
            item.description = cur_item.description
            item.bl_idname = cur_item.bl_idname

            for cur_prop_item in cur_item.prop_list:
                prop_item = item.prop_list.add()
                prop_item.name = cur_prop_item.name
                prop_item.value = cur_prop_item.value

            pref.weight_list_index = len(pref.weight_list) - 1

        elif self.action in {'UP', 'DOWN'}:
            my_list = pref.weight_list
            index = pref.weight_list_index
            neighbor = index + (-1 if self.action == 'UP' else 1)
            my_list.move(neighbor, index)
            self.move_index(context)

        return {'FINISHED'}

    def move_index(self, context):
        pref = get_pref()
        index = pref.weight_list_index
        new_index = index + (-1 if self.action == 'UP' else 1)
        pref.weight_list_index = max(0, min(new_index, len(pref.weight_list) - 1))


class ADJT_OT_WeightListAdd(ListAction, bpy.types.Operator):
    bl_idname = "adjt.weight_list_add"
    bl_label = "Add"

    action = 'ADD'


class ADJT_OT_WeightListRemove(ListAction, bpy.types.Operator):
    bl_idname = "adjt.weight_list_remove"
    bl_label = "Remove"

    action = 'REMOVE'


class ADJT_OT_WeightListCopy(ListAction, bpy.types.Operator):
    bl_idname = "adjt.weight_list_copy"
    bl_label = "Copy Config"

    action = 'COPY'


class ADJT_OT_WeightListMoveUP(ListAction, bpy.types.Operator):
    bl_idname = "adjt.weight_list_move_up"
    bl_label = 'Move Up'

    action = 'UP'


class ADJT_OT_WeightListMoveDown(ListAction, bpy.types.Operator):
    bl_idname = "adjt.weight_list_move_down"
    bl_label = 'Move Down'

    action = 'DOWN'


class ADJT_OT_CheckWeight(bpy.types.Operator):
    bl_label = "Check Weight"
    bl_idname = "mesh.adjt_check_weight"
    bl_options = {"UNDO", "INTERNAL"}

    # data
    obj = None

    check_type: EnumProperty(name='Type', items=[
        ('VOLUME', 'Volume', 'Volume * Density'),
        ('AREA', 'Area', 'Area * Thickness * Density'),
    ])

    area_thickness: FloatProperty(name='Thickness', default=0.13)

    precision: IntProperty(name='Precision', default=2, min=0, max=5)

    mat_list = [(19.32, 'Yellow Gold 24K', 'Au 99.9%'),
                (10.36, 'Silver Sterling', 'Ag 92.5%, Cu 7.5%'),
                (1, 'Wax', ''), ]

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        row = layout.row(align=True)
        row.prop(self, 'check_type', expand=True)
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

        pref = get_pref()
        mat_list = pref.weight_list
        precision = self.precision

        def draw_ans(self, context):
            layout = self.layout

            layout.operator('adjt.clip_board', text=f"{volume_fmt}³").data = str(volume_fmt)
            layout.separator()
            for mat in mat_list:
                if not mat.use: continue
                data = str(round(mat.density * eval(volume_str) / 1000, precision))
                layout.operator('adjt.clip_board', text=f'{mat.name}: {data}g').data = f'{mat.name}: {data}g'

        context.window_manager.popup_menu(draw_func=draw_ans, title='Result', icon='INFO')

        return {"FINISHED"}


def register():
    bpy.utils.register_class(ADJT_OT_CheckWeight)

    bpy.utils.register_class(ADJT_UL_WeightList)
    bpy.utils.register_class(ADJT_OT_WeightListAdd)
    bpy.utils.register_class(ADJT_OT_WeightListRemove)
    bpy.utils.register_class(ADJT_OT_WeightListCopy)
    bpy.utils.register_class(ADJT_OT_WeightListMoveUP)
    bpy.utils.register_class(ADJT_OT_WeightListMoveDown)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_CheckWeight)

    bpy.utils.unregister_class(ADJT_UL_WeightList)
    bpy.utils.unregister_class(ADJT_OT_WeightListAdd)
    bpy.utils.unregister_class(ADJT_OT_WeightListRemove)
    bpy.utils.unregister_class(ADJT_OT_WeightListCopy)
    bpy.utils.unregister_class(ADJT_OT_WeightListMoveUP)
    bpy.utils.unregister_class(ADJT_OT_WeightListMoveDown)
