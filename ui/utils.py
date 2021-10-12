def check_unit(context):
    unit = context.scene.unit_settings

    if unit.system == "METRIC" and round(unit.scale_length, 4) != 0.001:
        return True

    if unit.system == "IMPERIAL":
        return True

    return False


def t3dn_bip_convert(path):
    import os
    path = path.replace('\\','/')
    src_lst = []

    for file in os.listdir(path):
        if file.endswith('.png'):
            src_lst.append(file)

    tgz_lst = [filepath.removesuffix('.png') + '.bip' for filepath in src_lst]

    for idx, file_name in enumerate(src_lst):
        os.system(f'cd {path} & python -m t3dn_bip_converter {src_lst[idx]} {tgz_lst[idx]}')

# t3dn_bip_convert(r'C:\Users\atticus\AppData\Roaming\Blender Foundation\Blender\3.0\scripts\addons\ad_jewl_tools\ui\icons\\')