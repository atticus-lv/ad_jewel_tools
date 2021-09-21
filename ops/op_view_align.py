import bpy
import os
from bpy.props import StringProperty
from .. import __folder_name__

from .op_utils import ADJT_OT_ModalTemplate


class ADJT_OT_ViewAlign(ADJT_OT_ModalTemplate):
    '''Copy the select obj to align view
选择并复制当前物体为三视图'''
    bl_label = "View Align"
    bl_idname = "adjt.view_align"
    bl_options = {'REGISTER', 'GRAB_CURSOR', 'BLOCKING', 'UNDO'}

    object = None
    display_ob = None
    node_group_name: StringProperty(name='Node Group Name', default='Horizontal 4 View')

    # props
    separate = 0.2

    @classmethod
    def poll(self, context):
        if context.active_object:
            return len(context.selected_objects) == 1 and context.active_object.type == 'MESH'

    def finish(self, context):
        if self._cancel and not self._finish:
            if self.display_ob:
                bpy.data.objects.remove(self.display_ob)
                self.display_ob = None
            if self.object.hide_render == 1:
                self.object.hide_render = 0
                self.object.hide_set(False)

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
        self.cursor_set = True

    def main(self, context):
        # set and hide origin obj
        self.object = context.active_object
        self.object.hide_render = 1
        self.object.hide_set(True)

        # extra ob for display
        self.display_ob = self.create_obj()
        self.display_ob.name = 'ADJT_Render'
        mod = self.display_ob.modifiers.new(name='ViewAlign', type='NODES')
        mod.node_group = self.get_preset(node_group_name=self.node_group_name)
        if 'View Align Dep' not in context.scene.collection.children:
            dep_coll_dir = bpy.data.collections.new("View Align Dep")
            context.scene.collection.children.link(dep_coll_dir)
        else:
            dep_coll_dir = context.scene.collection.children['View Align Dep']

        context.collection.objects.unlink(self.display_ob)
        dep_coll_dir.objects.link(self.display_ob)

        # tips
        self.tips.clear()
        self.tips.append(f'')
        self.tips.append(f'Apply "{self.node_group_name}" preset')

        # set obj
        nt = mod.node_group
        node = nt.nodes.get('Group')
        ob_ip = node.inputs.get('Object')
        ob_ip.default_value = self.object

        self.separate = node.inputs[0]  # the first socket

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

    def create_obj(self):
        vertices = edges = faces = []
        new_mesh = bpy.data.meshes.new('adjt_empty_mesh')
        new_mesh.from_pydata(vertices, edges, faces)
        new_mesh.update()
        obj = bpy.data.objects.new('new_object', new_mesh)
        bpy.context.collection.objects.link(obj)

        return obj


def register():
    bpy.utils.register_class(ADJT_OT_ViewAlign)


def unregister():
    bpy.utils.unregister_class(ADJT_OT_ViewAlign)
