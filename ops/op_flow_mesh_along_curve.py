import bpy
import bgl, blf, gpu

from .op_utils import ADJT_OT_ModalTemplate
from .utils import DrawMsgHelper, est_curve_length
from bpy.props import BoolProperty, EnumProperty

# base info


deform_axis_dict = {
    'POS_X': 'X',
    'POS_Y': 'Y',
    'POS_Z': 'Z',
    'NEG_X': '-X',
    'NEG_Y': '-Y',
    'NEG_Z': '-Z',
}


def draw_move_object_callback_px(self, context):
    msg = DrawMsgHelper(0, self.color, self.alpha)

    x_align, y_align = msg.get_region_size(0.5, 0.03)

    top = 150
    step = 20

    if self.mod_array:
        length = 1
        for l in self.mod_array.relative_offset_displace:
            if l != 0:
                length = l
                break
        self.array_count = int(self.curve_len / length)

    array = 'Array: ' + str(self.array_direction)
    curve = 'Curve: ' + str(deform_axis_dict[self.deform_axis_list[self.deform_axis_index]])
    text = array + ' | ' + curve + ' ' + 'Num: ' + str(self.array_count)

    msg.draw_title(x=x_align - msg.get_text_length(text) * 1.15, y=y_align + top, text=text, size=30)

    for i, t in enumerate(self.tips):
        offset = 0.5 * msg.get_text_length(self.tips[i])
        msg.draw_info(x=x_align - offset, y=y_align + top - step * (i + 1), text=self.tips[i], size=15)


class ADJT_OT_FlowMeshAlongCurve(bpy.types.Operator):
    """First select mesh then add select curve
先选网格物体再加选曲线"""
    bl_idname = "adjt.flow_mesh_along_curve"
    bl_label = "Flow mesh along curve"
    bl_options = {'REGISTER', 'GRAB_CURSOR', 'BLOCKING', 'UNDO'}

    # user option
    use_array: BoolProperty(name='Use Array', default=True)

    # object
    ori_mesh = None
    ori_curve = None

    mod_array = None
    mod_curve = None

    # modifier
    tmp_array_offset = [1, 1, 1]
    array_direction = 'X'

    deform_axis_list = [
        'POS_X',
        'POS_Y',
        'POS_Z',
        'NEG_X',
        'NEG_Y',
        'NEG_Z',
    ]
    deform_axis_index = 0

    # state
    _finish = BoolProperty(default=False)
    _cancel = BoolProperty(default=False)

    # UI
    tips = [
        '',
        'A to toggle Array, X/Y/Z to switch direction',
        'Wheel UP/Down to Curve deform axis',
        'Left to Confirm / Right to Cancel',
    ]

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'CURVE' and len(context.selected_objects) == 2

    def append_handle(self, context):
        # append handle
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_move_object_callback_px, args, 'WINDOW',
                                                              'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

    def remove_handle(self, context, cancel):
        context.window_manager.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

        return {'FINISHED'} if cancel else {'CANCELLED'}

    def finish(self, context):
        # draw Handle
        if self.cursor_set:
            context.window.cursor_modal_restore()
            context.area.tag_redraw()
        # modifier
        self.remove_modifiers()
        # set active object
        if self._cancel and context.active_object != self.ori_curve:
            context.view_layer.objects.active = self.ori_curve
        elif not self._cancel and context.active_object != self.ori_mesh:
            context.view_layer.objects.active = self.ori_mesh


    def modal(self, context, event):
        context.area.tag_redraw()

        # draw timer
        if event.type == 'TIMER':
            # fade drawing
            if self._cancel or self._finish:
                self.finish(context)

                if self.alpha > 0:
                    self.alpha -= 0.04  # fade
                else:
                    return self.remove_handle(context, cancel=self._cancel)

        if event.type == "MIDDLEMOUSE" or (
                (event.alt or event.shift or event.ctrl) and event.type == "MIDDLEMOUSE"):
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE':
            self._finish = True

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._cancel = True

        elif event.type == "A" and event.value == "PRESS" and self.mod_array:
            self.use_array = True if self.use_array == False else False
            self.mod_array.show_viewport = True if self.use_array else False

        # deform axis
        elif event.type == "WHEELUPMOUSE" and not (self._cancel or self._finish):
            self.deform_axis_index -= 1
            if self.deform_axis_index < 0: self.deform_axis_index = 5
            self.mod_curve.deform_axis = self.deform_axis_list[self.deform_axis_index]

        elif event.type == "WHEELDOWNMOUSE" and not (self._cancel or self._finish):
            self.deform_axis_index += 1
            if self.deform_axis_index > 5: self.deform_axis_index = 0
            self.mod_curve.deform_axis = self.deform_axis_list[self.deform_axis_index]

        # array values
        elif event.type == 'MOUSEMOVE' and not (self._cancel or self._finish):
            self.mouseDX = self.mouseDX - event.mouse_x
            self.mouseDY = self.mouseDY - event.mouse_y

            multiplier = 0.001 if event.shift else 0.005
            # multi offset
            offset = self.mouseDX

            if self.array_direction == 'X':
                self.mod_array.relative_offset_displace[0] -= offset * multiplier
            elif self.array_direction == 'Y':
                self.mod_array.relative_offset_displace[1] -= offset * multiplier
            else:
                self.mod_array.relative_offset_displace[2] -= offset * multiplier

            # reset
            self.mouseDX = event.mouse_x
            self.mouseDY = event.mouse_y

        # array axis
        elif event.type in {'X', 'Y', 'Z'} and not (self._cancel or self._finish):
            # save to cache
            self.tmp_array_offset[0] = self.mod_array.relative_offset_displace[0]
            self.tmp_array_offset[1] = self.mod_array.relative_offset_displace[1]
            self.tmp_array_offset[2] = self.mod_array.relative_offset_displace[2]

            if event.type == 'X' and event.value == "PRESS":
                self.mod_array.relative_offset_displace[1] = 0
                self.mod_array.relative_offset_displace[2] = 0

            elif event.type == 'Y' and event.value == "PRESS":
                self.mod_array.relative_offset_displace[0] = 0
                self.mod_array.relative_offset_displace[2] = 0

            elif event.type == 'Z' and event.value == "PRESS":
                self.mod_array.relative_offset_displace[0] = 0
                self.mod_array.relative_offset_displace[1] = 0
            # set direction
            self.array_direction = event.type

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # set modifier
        self.ori_curve = context.active_object
        self.ori_mesh = [obj for obj in context.selected_objects if obj != self.ori_curve][0]
        self.mod_array, self.mod_curve = self.add_modifiers()

        # mesh & mod
        context.view_layer.objects.active = self.ori_mesh
        self.array_direction = 'X'
        self.curve_len = est_curve_length(self.ori_curve)
        self.array_count = 0

        # modal
        self._finish = False
        self._cancel = False

        self.color = 1, 1, 1
        self.alpha = 0.8
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y

        # icon
        self.cursor_set = True
        context.window.cursor_modal_set('MOVE_X')

        self.append_handle(context)
        return {'RUNNING_MODAL'}

    def remove_modifiers(self):
        if self.use_array is False and self.mod_array:

            self.ori_mesh.modifiers.remove(self.mod_array)
            self.mod_array = None

        if self._cancel and not self._finish:
            if self.mod_array:
                self.ori_mesh.modifiers.remove(self.mod_array)
                self.mod_array = None

            if self.mod_curve:
                self.ori_mesh.modifiers.remove(self.mod_curve)
                self.mod_curve = None

    def add_modifiers(self):
        mod_array = self.ori_mesh.modifiers.new(name='Array', type='ARRAY')
        mod_array.fit_type = 'FIT_CURVE'
        mod_array.curve = self.ori_curve
        mod_array.use_merge_vertices = True
        mod_array.use_merge_vertices_cap = True

        mod_curve = self.ori_mesh.modifiers.new(name='Curve', type='CURVE')
        mod_curve.object = self.ori_curve
        return mod_array, mod_curve


def register():
    bpy.utils.register_class(ADJT_OT_FlowMeshAlongCurve)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_FlowMeshAlongCurve)
