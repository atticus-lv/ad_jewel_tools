def check_unit(context):
    unit = context.scene.unit_settings

    if unit.system == "METRIC" and round(unit.scale_length, 4) != 0.001:
        return True

    if unit.system == "IMPERIAL":
        return True

    return False


import os


def t3dn_bip_convert_batch(dir):
    dir = dir.replace('\\', '/')
    src_lst = []

    for file in os.listdir(dir):
        if file.endswith('.png'):
            src_lst.append(file)

    tgz_lst = [filepath.removesuffix('.png') + '.bip' for filepath in src_lst]

    for idx, file_name in enumerate(src_lst):
        os.system(f'cd {dir} & python -m t3dn_bip_converter {src_lst[idx]} {tgz_lst[idx]}')


def t3dn_bip_convert(src, tgz):
    dir = os.path.dirname(src)
    dir = dir.replace('\\', '/')
    os.system(f'cd {dir} & python -m t3dn_bip_converter {src} {tgz}')
# #
# t3dn_bip_convert_batch(r'C:\Users\atticus\AppData\Roaming\Blender Foundation\Blender\3.0\scripts\addons\ad_jewl_tools\ui\icons\\')
# t3dn_bip_convert_batch(r'C:\Users\atticus\AppData\Roaming\Blender Foundation\Blender\3.0\scripts\addons\ad_jewl_tools\preset\node_groups\thumb\animate\\')
# t3dn_bip_convert_batch(r'C:\Users\atticus\AppData\Roaming\Blender Foundation\Blender\3.0\scripts\addons\ad_jewl_tools\preset\node_groups\thumb\view align\\')
