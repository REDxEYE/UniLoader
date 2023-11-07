import traceback
from pathlib import Path
from importlib import import_module
from types import ModuleType
from typing import Any, Callable

import bpy

from bpy.props import (BoolProperty, CollectionProperty, EnumProperty,
                       FloatProperty, StringProperty)
from bpy.types import Operator, AddonPreferences

from .common_api import PluginInfo, LoaderInfo

bl_info = {
    "name": "UniLoader",
    "author": "RED_EYE",
    "version": (0, 1, 0),
    "blender": (3, 1, 0),
    "location": "File > Import > UniLoader",
    "description": "Addon that provide api for other importers(UniLoader sub-addons).",
    "category": "Import"
}
PLUGINS: dict[str, tuple[ModuleType, list[tuple[LoaderInfo, Any]]]] = {}


class UniLoader_OT_ImportTemplate(Operator):
    """Importer template"""
    bl_idname = "uniloader.template"
    bl_label = "Import template"
    bl_options = {'UNDO'}

    filepath: StringProperty(
        subtype='FILE_PATH',
    )
    files: CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob: StringProperty(default="*.placeholder", options={'HIDDEN'})
    import_func: Callable[[str, list[str]], set[str]]

    def execute(self, context):
        return self.import_func(self.filepath, [file.name for file in self.files])

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UniLoader_MT_Menu(bpy.types.Menu):
    bl_label = "UniLoader plugins"
    bl_idname = "uniloader.menu"

    def draw(self, context):
        layout = self.layout
        for module, loaders in PLUGINS.values():
            for loader, operator in loaders:
                layout.operator(operator.bl_idname, text=loader["name"])


class UniLoaderAddonPreferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Registered plugins")
        box = layout.box()
        for module, _ in PLUGINS.values():
            sub_box = box.box()
            row = sub_box.row(align=True)
            row.label(text="Name: ")
            row.label(text=module.plugin_info["name"])


CLASSES = [UniLoader_MT_Menu, UniLoaderAddonPreferences, ]

uniloader_folder_name = Path(__file__).absolute().parent.stem
plugins_dir = Path(__file__).absolute().parent / "plugins"
for plugin_dir in plugins_dir.iterdir():
    try:
        plugin = import_module(".plugins." + plugin_dir.stem, uniloader_folder_name)
        plugin_info: PluginInfo = plugin.plugin_info
    except Exception as e:
        print(f"Failed to load {plugin_dir.stem} due to {e}:")
        traceback.print_exc()
        continue
    print(f"Loaded sub-plugin \"{plugin_info['name']}\"")
    plugin.plugin_init()
    loaders = []
    for loader in plugin_info["loaders"]:
        plugin_operator = type(f"UniLoader_OT_Import{plugin_dir.stem.upper()}", (UniLoader_OT_ImportTemplate,),
                               {
                                   "import_func": loader["import_fn"],
                                   "bl_idname": f"uniloader.{loader['id']}",
                                   "bl_label": loader["name"]
                               })
        annotations = plugin_operator.__annotations__
        annotations["filter_glob"] = StringProperty(default=";".join(loader["exts"]), options={'HIDDEN'})
        for prop in loader["properties"]:
            t = prop["bl_type"]
            annotations[prop["prop_name"]] = t(name=prop["name"], **prop["kwargs"])
        loaders.append((loader, plugin_operator))
        CLASSES.append(plugin_operator)
    PLUGINS[plugin_info["name"]] = plugin, loaders

register_, unregister_ = bpy.utils.register_classes_factory(CLASSES)


def menu_import(self, context):
    self.layout.menu(UniLoader_MT_Menu.bl_idname)


def register():
    register_()
    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    unregister_()
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
