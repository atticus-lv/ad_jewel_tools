bl_info = {
    "name": "AD的珠宝小工具",
    "author": "Atticus",
    "version": (0, 1),
    "blender": (2, 93, 0),
    "location": "3D View > Side Panel",
    "description": "一些辅助建模的小工具合集",
    'warning': "持续开发中",
    # "doc_url"    : "https://atticus-lv.github.io/RenderStackNode/#/",
    "category": "Model",
}

from . import ops, ui


def register():
    ops.register()
    ui.register()
