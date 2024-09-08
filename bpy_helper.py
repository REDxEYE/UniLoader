import bpy


def is_blender_4():
    return bpy.app.version >= (4, 0, 0)


def is_blender_4_1():
    return bpy.app.version >= (4, 1, 0)
