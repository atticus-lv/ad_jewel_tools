import time

import bpy
from bpy.props import BoolProperty

import bgl, blf, gpu
from gpu_extras.batch import batch_for_shader

from .utils import DrawMsgHelper, DrawHandle
from .utils import draw_pre, draw_post, draw_round_rectangle, draw_nurbs_curve


def draw_template_callback_px(self, context):
    draw_pre()

    msg = DrawMsgHelper(0, self.color, self.alpha)

    x_align, y_align = msg.get_region_size(0.5, 0.03)  # middle start_pos point
    y_align = y_align + 150  # top start_pos point

    text = self.bl_label if self.title == '' else self.title
    title_width = msg.get_text_length(text)
    title_height = msg.get_text_height(text)

    background_width = 400
    background_height = background_width * 0.382

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

    # draw background
    vertices = (
        (x_align + background_width / 2, y_align + background_height / 2),  # right top
        (x_align - background_width / 2, y_align + background_height / 2),  # left top
        (x_align - background_width / 2, y_align - background_height / 2),  # left bottom
        (x_align + background_width / 2, y_align - background_height / 2),  # right bottom
    )
    inner = 3
    shadow_vertices = (
        (x_align + background_width / 2 - inner, y_align + background_height / 2 - inner),  # right top
        (x_align - background_width / 2 + inner, y_align + background_height / 2 - inner),  # left top
        (x_align - background_width / 2 + inner, y_align - background_height / 2 + inner),  # left bottom
        (x_align + background_width / 2 - inner, y_align - background_height / 2 + inner),  # right bottom
    )

    draw_round_rectangle(shader, vertices, color=(0.1, 0.1, 0.1, self.alpha * 0.5), radius=20)
    draw_round_rectangle(shader, shadow_vertices, color=(0, 0, 0, self.alpha * 0.5), radius=20)

    # draw text
    msg.draw_title(x=x_align - title_width * 1.15,
                   y=y_align + background_height / 2 - title_height * 2,
                   text=text, size=30)

    for i, t in enumerate(self.tips):
        text = self.tips[i]
        offset = 0.5 * msg.get_text_length(text)
        height = msg.get_text_height(text)
        msg.draw_info(x=x_align - offset, y=y_align - height * 1.5 * (len(self.tips) - i), text=text, size=18)

    draw_post()


def end(self, context):
    # draw Handle
    if self.cursor_set:
        context.window.cursor_modal_restore()
        context.area.tag_redraw()
    if self._finish:
        self.title = 'Confirm!'
    elif self._cancel:
        self.title = 'Cancel!'


# TODO replace current modal template with normal and add new draw ui template after executing current
from .runtime import draw_handle
from .runtime import reset_draw, start_time, start_fade
from .runtime import draw_tips, draw_title


class Shader():
    def __init__(self, context, draw_title: str, draw_tips: list[str], width=1):
        self.title = draw_title
        self.tips = draw_tips
        self.width = width
        self.context = context
        self.fade_time = 3
        self.color = 1,1,1
        self.alpha = 0.8

    def append_handle(self):
        global draw_handle
        draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw, (self.context,), "WINDOW", "POST_PIXEL")

    def remove_handle(self):
        global draw_handle

        if draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(draw_handle, "WINDOW")
            draw_handle = None

    def set_fade(self):
        if start_fade is True:
            pass

    def draw(self, context):
        draw_pre(self.width)

        msg = DrawMsgHelper(0, self.color, self.alpha)

        x_align, y_align = msg.get_region_size(0.5, 0.03)  # middle start_pos point
        y_align = y_align + 150  # top start_pos point

        text = self.title
        title_width = msg.get_text_length(text)
        title_height = msg.get_text_height(text)

        background_width = 400
        background_height = background_width * 0.382

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')

        # draw background
        vertices = (
            (x_align + background_width / 2, y_align + background_height / 2),  # right top
            (x_align - background_width / 2, y_align + background_height / 2),  # left top
            (x_align - background_width / 2, y_align - background_height / 2),  # left bottom
            (x_align + background_width / 2, y_align - background_height / 2),  # right bottom
        )
        inner = 3
        shadow_vertices = (
            (x_align + background_width / 2 - inner, y_align + background_height / 2 - inner),  # right top
            (x_align - background_width / 2 + inner, y_align + background_height / 2 - inner),  # left top
            (x_align - background_width / 2 + inner, y_align - background_height / 2 + inner),  # left bottom
            (x_align + background_width / 2 - inner, y_align - background_height / 2 + inner),  # right bottom
        )

        draw_round_rectangle(shader, vertices, color=(0.1, 0.1, 0.1, self.alpha * 0.5), radius=20)
        draw_round_rectangle(shader, shadow_vertices, color=(0, 0, 0, self.alpha * 0.5), radius=20)

        # draw text
        msg.draw_title(x=x_align - title_width * 1.15,
                       y=y_align + background_height / 2 - title_height * 2,
                       text=text, size=30)

        for i, t in enumerate(self.tips):
            text = self.tips[i]
            offset = 0.5 * msg.get_text_length(text)
            height = msg.get_text_height(text)
            msg.draw_info(x=x_align - offset, y=y_align - height * 1.5 * (len(self.tips) - i), text=text, size=18)

        draw_pre()


class ADJT_OT_DrawUI(bpy.types.Operator):
    bl_label = 'Draw UI'
    bl_idname = 'adjt.draw_ui'
    bl_options = {"INTERNAL"}

    shader = None

    def invoke(self, context, event):
        start_time = time.time()
        self.shader = Shader(context, draw_title, draw_tips)
        self.shader.append_handle()

        self.timer = context.window_manager.event_timer_add(0.025, window=context.window)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area != None:
            context.area.tag_redraw()

        if time.time() - start_time > self.shader.fade_time: self.finished(context)

        self.shader.draw(context)

        return {'PASS_THROUGH'}

    def finished(self, context):
        '''Remove the timer, shader, and reset Data'''
        print('finished drawing')
        if self.timer is not None:
            context.window_manager.event_timer_remove(self.timer)

        if context.area is not None:
            context.area.tag_redraw()

        if self.shader is not None:
            self.shader.remove_handle()


class ADJT_OT_NormalTemplate(bpy.types.Operator):
    bl_label = "ADJT Title"
    bl_options = {'REGISTER', 'UNDO'}

    # state
    _finish = BoolProperty(update=end)
    _cancel = BoolProperty(update=end)
    cursor_set = False

    # UI
    ui_delay = 0.4

    title = ''
    tips = [
        '',
    ]

    # draw objects
    draw_curves = []
    draw_meshes = []

    def draw_ui(self, context,title,tips):
        global draw_title,draw_tips
        draw_title = title
        draw_tips = tips
        bpy.ops.adjt.draw_ui('INVOKE_DEFAULT')

    def execute(self, context):
        return {'FINISHED'}

    def modal(self, context, event):
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        return self.execute(context)


class ADJT_OT_ModalTemplate(bpy.types.Operator):
    bl_label = "ADJT Title"
    bl_options = {'REGISTER', 'UNDO'}

    # state
    _finish = BoolProperty(update=end)
    _cancel = BoolProperty(update=end)
    cursor_set = False

    # UI
    ui_delay = 0.4

    title = ''
    tips = [
        '',
    ]

    # draw objects
    draw_curves = []
    draw_meshes = []

    def remove_handle(self, context):
        context.window_manager.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

        return {'CANCELLED'} if self._cancel else {'FINISHED'}

    def append_handle(self, context):
        # icon
        if self.cursor_set == True:
            context.window.cursor_modal_set('MOVE_X')

        # append handle
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_template_callback_px, args, 'WINDOW',
                                                              'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

    def restore_cursor(self, context):
        if self.cursor_set:
            self.cursor_set = False
            context.window.cursor_modal_restore()

    def pre(self, context, event):
        pass

    def main(self, context):
        self._finish = True

    def execute(self, context):
        try:
            self.main(context)
        except Exception as e:
            self.report({"ERROR"}, str(e))
            self._cancel = True
        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        context.area.tag_redraw()
        # draw timer
        if event.type == 'TIMER':
            # fade drawing
            if self._cancel or self._finish:
                # context.window.cursor_modal_restore()
                if self.ui_delay > 0:
                    self.ui_delay -= 0.01
                else:
                    if self.alpha > 0:
                        self.alpha -= 0.02  # fade
                    else:
                        return self.remove_handle(context)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.pre(context, event)
        # modal
        self._finish = False
        self._cancel = False
        self.color = 1, 1, 1
        self.alpha = 0.8
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y

        self.append_handle(context)
        return self.execute(context)


def register():
    bpy.utils.register_class(ADJT_OT_DrawUI)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_DrawUI)
