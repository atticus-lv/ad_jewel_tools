def is_right_unit(context):
    unit = context.scene.unit_settings

    if unit.system == "METRIC" and round(unit.scale_length, 4) != 0.001:
        return

    if unit.system == "IMPERIAL":
        return

    return True
