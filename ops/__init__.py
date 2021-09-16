import bpy
import os
import importlib

# Register information
##################
not_register_file = {'__init__.py'}
not_register_cls = {}
start_file_id = 'op'
start_class_id = 'ADJT'

#################

tree = [x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x.endswith('.py') and x not in not_register_file]

for i in tree:
    importlib.import_module('.' + i, package=__package__)

__globals = globals().copy()

classed = set()

for num_id, x in enumerate([x for x in __globals if x.startswith(start_file_id)]):
    for y in [item for item in dir(__globals[x]) if item.startswith(start_class_id) and item not in not_register_cls]:
        classed.add(getattr(__globals[x], y))

classed = list(classed)


def register():
    from bpy.utils import register_class

    for cls in classed:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    dependent_classes = set()

    for cls in reversed(classed):
        unregister_class(cls)

    for cls in classed:
        for x in cls.dependent_classes:
            dependent_classes.add(x)

    for cls in dependent_classes:
        unregister_class(cls)
