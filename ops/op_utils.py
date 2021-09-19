import bpy
import bgl, blf, gpu
from gpu_extras.batch import batch_for_shader

from .utils import DrawHelper
from bpy.props import BoolProperty


def draw_template_callback_px(self, context):
    bgl.glLineWidth(1)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    bgl.glHint(bgl.GL_LINE_SMOOTH_HINT, bgl.GL_NICEST)

    msg = DrawHelper(0, self.color, self.alpha)

    x_align, y_align = msg.get_region_size(0.5, 0.03)

    top = 150
    step = 20
    backgroud_width = 500
    backgroud_height = backgroud_width * 0.382

    vertices = (
        (x_align - backgroud_width / 2, y_align + top + backgroud_height / 2),  # left top
        (x_align + backgroud_width / 2, y_align + top + backgroud_height / 2),  # right top
        (x_align - backgroud_width / 2, y_align + top - backgroud_height / 2),  # left bottom
        (x_align + backgroud_width / 2, y_align + top - backgroud_height / 2))  # right bottom

    indices = ((0, 1, 3), (0, 2, 3))

    # draw backgroud
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", (0, 0, 0, self.alpha * 0.5))
    batch.draw(shader)

    # draw text
    text = self.bl_label

    msg.draw_title(x=x_align - msg.get_text_length(text), y=y_align + top, text=text, size=30)

    for i, t in enumerate(self.tips):
        offset = 0.5 * msg.get_text_length(self.tips[i])
        msg.draw_info(x=x_align - offset, y=y_align + top - step * (i + 1), text=self.tips[i], size=15)

    # restore
    #####################
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)


def finish(self, context):
    # draw Handle
    if self.cursor_set:
        context.window.cursor_modal_restore()
        context.area.tag_redraw()


class ADJT_OT_ModalTemplate(bpy.types.Operator):
    bl_label = "ADJT Title"
    bl_options = {'REGISTER', 'UNDO'}

    # state
    _finish = BoolProperty(update=finish)
    _cancel = BoolProperty(update=finish)
    cursor_set = False

    # UI
    ui_delay = 0.2
    tips = [
        '',
    ]

    def remove_handle(self, context, cancel):
        context.window_manager.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

        return {'FINISHED'} if cancel else {'CANCELLED'}

    def append_handle(self, context):
        # icon
        # self.cursor_set = True
        # context.window.cursor_modal_set('MOVE_X')

        # append handle
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_template_callback_px, args, 'WINDOW',
                                                              'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

    def main(self, context):
        self._finish = True

    def execute(self, context):
        self.main(context)

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
                        self.alpha -= 0.01  # fade
                    else:
                        return self.remove_handle(context, cancel=self._cancel)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # modal
        self._finish = False
        self._cancel = False
        self.color = 1, 1, 1
        self.alpha = 0.8
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y

        self.append_handle(context)
        return self.execute(context)
