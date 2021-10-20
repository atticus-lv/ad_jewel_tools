import bpy
import os
from bpy.props import StringProperty
from ... import __folder_name__

from ..ops_utils.op_template import ADJT_OT_ModalTemplate


class ADJT_OT_ViewAlign(ADJT_OT_ModalTemplate):
    '''Copy the select obj to align view
选择并复制当前物体为三视图'''
    bl_label = "View Align"
    bl_idname = "node.adjt_view_align"
    bl_options = {'REGISTER', 'UNDO'}

    display_ob = None
    mod = None
    mod_remove = True
    node_group_name: StringProperty(name='Node Group Name', default='Horizontal 4 View')

    # props
    separate = 0.2

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'

    def finish(self, context):
        if self._cancel and self.mod_remove is not None:
            self.display_ob.modifiers.remove(self.mod)
            self.mod_remove = None
        self.restore_cursor(context)

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'TIMER':
            # fade drawing
            if self._cancel or self._finish:
                self.finish(context)

                if self.ui_delay > 0:
                    self.ui_delay -= 0.01
                else:
                    if self.alpha > 0:
                        self.alpha -= 0.02  # fade
                    else:
                        return self.remove_handle(context)

        if self._finish or self._cancel:
            return {'PASS_THROUGH'}

        elif event.type in {"MIDDLEMOUSE", 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or (
                (event.alt or event.shift or event.ctrl) and event.type == "MIDDLEMOUSE"):
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE':
            self._finish = True

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._cancel = True

        elif event.type == 'MOUSEMOVE':
            self.mouseDX = self.mouseDX - event.mouse_x
            self.mouseDY = self.mouseDY - event.mouse_y

            speed = 0.05 / 10 if event.shift else 0.05
            # multi offset
            offset = self.mouseDX
            self.separate.default_value -= offset * speed
            # reset
            self.mouseDX = event.mouse_x
            self.mouseDY = event.mouse_y

        return {"RUNNING_MODAL"}

    def pre(self, context, event):
        self.mod_remove = True
        self.cursor_set = True

    def main(self, context):
        self.display_ob = context.active_object
        self.mod = self.display_ob.modifiers.new(name='ADJT_ViewAlign', type='NODES')
        self.mod.node_group = self.get_preset(node_group_name=self.node_group_name)
        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Apply "{self.node_group_name}" preset')

        # set obj
        nt = self.mod.node_group
        node = nt.nodes.get('Group')

        self.separate = node.inputs['Separate']  # the first socket

        return {"RUNNING_MODAL"}

    def get_preset(sellf, node_group_name):
        base_dir = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', __folder_name__, 'preset',
                                'node_groups',
                                'view_align_preset.blend')

        node_group_dir = os.path.join(base_dir, 'NodeTree') + '/'

        if node_group_name in bpy.data.node_groups:
            preset_node = bpy.data.node_groups[node_group_name]
        else:
            bpy.ops.wm.append(filename=node_group_name, directory=node_group_dir)
            preset_node = bpy.data.node_groups[node_group_name]

        return preset_node


def register():
    bpy.utils.register_class(ADJT_OT_ViewAlign)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ViewAlign)
