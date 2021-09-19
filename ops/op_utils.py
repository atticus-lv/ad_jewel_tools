import bpy
import bgl, blf, gpu

from .utils import DrawHelper
from bpy.props import BoolProperty


def draw_template_callback_px(self, context):
    msg = DrawHelper(0, self.color, self.alpha)

    x_align, y_align = msg.get_region_size(0.5, 0.03)

    top = 150
    step = 20

    text = self.title

    msg.draw_title(x=x_align - msg.get_text_length(text), y=y_align + top, text=text)

    for i, t in enumerate(self.tips):
        offset = 0.5 * msg.get_text_length(self.tips[i])
        msg.draw_info(x=x_align - offset, y=y_align + top - step * (i + 1), text=self.tips[i])


def finish(self, context):
    # draw Handle
    if self.cursor_set:
        context.window.cursor_modal_restore()
        context.area.tag_redraw()


class ADJT_OT_ModalTemplate(bpy.types.Operator):
    bl_label = "Flow mesh along curve"
    bl_options = {'REGISTER', 'UNDO'}

    # state
    _finish = BoolProperty(update=finish)
    _cancel = BoolProperty(update=finish)
    cursor_set = False

    # UI
    title = 'ADJT Title'
    tips = [
        '',
        'tips 1'
        'tips 2'
        'tips 3'
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
                if self.alpha > 0:
                    self.alpha -= 0.015  # fade
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
