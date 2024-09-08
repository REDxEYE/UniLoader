import importlib
import os
import shutil
import sys
import traceback
import urllib.parse
from io import BytesIO
from pathlib import Path
from types import ModuleType
from typing import Any, Callable
from zipfile import ZipFile
import requests
import bpy

from bpy.props import (BoolProperty, CollectionProperty, EnumProperty,
                       FloatProperty, StringProperty)
from bpy.types import Operator, AddonPreferences

from .common_api import PluginInfo, LoaderInfo

if "UniLoader" not in sys.modules:
    sys.modules['UniLoader'] = sys.modules[Path(__file__).parent.stem]

bl_info = {
    "name": "UniLoader",
    "author": "RED_EYE",
    "version": (0, 1, 0),
    "blender": (3, 1, 0),
    "location": "File > Import > UniLoader",
    "description": "Addon that provide api for other importers(UniLoader sub-addons).",
    "category": "Import"
}
PLUGINS: dict[str, tuple[ModuleType, Any, list[tuple[LoaderInfo, Any]]]] = {}
uniloader_folder_name = Path(__file__).absolute().parent.stem
plugins_dir = Path(__file__).absolute().parent / "plugins"
os.makedirs(plugins_dir, exist_ok=True)


def _reload_module(name):
    if name in sys.modules:
        importlib.reload(sys.modules[name])


def _reload_module_recursive(base_name):
    for name in list(sys.modules.keys()):
        if name.startswith(base_name):
            _reload_module(name)


def _load_plugin(plugin_dirname: str):
    print(f"Trying to load \"{plugin_dirname}\" plugin")

    _reload_module_recursive(plugin_dirname)

    try:
        plugin = importlib.import_module(".plugins." + plugin_dirname, uniloader_folder_name)
        plugin_info: PluginInfo = plugin.plugin_info
    except Exception as e:
        print(f"Failed to load {plugin_dirname} due to {e}:")
        traceback.print_exc()
        return False
    print(f"Loaded sub-plugin \"{plugin_info['name']}\"")
    plugin.plugin_init()
    loaders = []
    new_classes = []
    operators = []
    for loader in plugin_info["loaders"]:
        plugin_operator = type(
            f"UniLoader_OT_Import{loader['id'].upper()}",
            (UniLoader_OT_ImportTemplate,),
            {
                "import_func": loader["import_fn"],
                "bl_idname": f"uniloader.{loader['id']}",
                "bl_label": loader["name"]
            }
        )
        operators.append((plugin_operator.bl_idname, loader["name"]))
        annotations = plugin_operator.__annotations__
        annotations["filter_glob"] = StringProperty(default=";".join(loader["exts"]), options={'HIDDEN'})
        for prop in loader["properties"]:
            t = prop["bl_type"]
            annotations[prop["prop_name"]] = t(name=prop["name"], **prop["kwargs"])
        loaders.append((loader, plugin_operator))
        new_classes.append(plugin_operator)

    plugin_menu_operator = type(
        f"UniLoader_MT_GroupMenu{plugin_info['id'].upper()}",
        (UniLoader_MT_GroupMenuTemplate,),
        {
            "operators": operators,
            "bl_idname": f"uniloader.menu_{plugin_info['id']}",
            "bl_label": plugin_info["name"]
        }
    )
    new_classes.append(plugin_menu_operator)
    PLUGINS[plugin_dirname] = plugin, plugin_menu_operator, loaders
    for cls in new_classes:
        bpy.utils.register_class(cls)
    return True


def _unload_plugin(plugin_dirname: str):
    print(f"Trying to unload \"{plugin_dirname}\" plugin")
    if plugin_dirname not in PLUGINS:
        return
    plugin, menu, loaders = PLUGINS[plugin_dirname]
    for _, operator in loaders:
        try:
            bpy.utils.unregister_class(operator)
        except RuntimeError:
            continue
    try:
        bpy.utils.unregister_class(menu)
    except RuntimeError:
        pass
    del PLUGINS[plugin_dirname]


def _delete_plugin(plugin_dirname: str):
    print(f"Deleting \"{plugin_dirname}\" plugin")
    if plugin_dirname in PLUGINS:
        _unload_plugin(plugin_dirname)
    if (plugins_dir / plugin_dirname).exists():
        shutil.rmtree(plugins_dir / plugin_dirname)


def _scan_plugins():
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    registered_addons = addon_prefs.addons

    known_addons = {addon.plugin_dir_name: addon for addon in registered_addons}

    # Reloading plugins if they were already loaded
    plugin_dirs = list(PLUGINS.keys())
    for plugin_dir in plugin_dirs:
        _unload_plugin(plugin_dir)

    if plugin_dirs:
        for plugin_dir_name in plugin_dirs:
            _load_plugin(plugin_dir_name)
            if plugin_dir_name in known_addons:
                plugin_info: PluginInfo = PLUGINS[plugin_dir_name][0].plugin_info
                addon_item = known_addons[plugin_dir_name]
                addon_item.name = plugin_info["name"]
                addon_item.id = plugin_info["id"]
                addon_item.version = "{}.{}.{}".format(*plugin_info["version"])
                addon_item.description = plugin_info.get("description", "")
                continue

            plugin_info = PLUGINS[plugin_dir_name][0].plugin_info
            addon_item = registered_addons.add()
            addon_item.name = plugin_info["name"]
            addon_item.id = plugin_info["id"]
            addon_item.version = "{}.{}.{}".format(*plugin_info["version"])
            addon_item.plugin_dir_name = plugin_dir_name
            addon_item.description = plugin_info.get("description", "")
            addon_item.enabled = True

    known_addons = {addon.plugin_dir_name: addon for addon in registered_addons}
    enabled_addons = [addon.plugin_dir_name for addon in registered_addons if addon.enabled]

    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.stem in known_addons:
            if plugin_dir.stem in enabled_addons:
                _load_plugin(plugin_dir.stem)
                plugin_info: PluginInfo = PLUGINS[plugin_dir.stem][0].plugin_info
                addon_item = known_addons[plugin_dir.stem]
                addon_item.name = plugin_info["name"]
                addon_item.id = plugin_info["id"]
                addon_item.version = "{}.{}.{}".format(*plugin_info["version"])
                addon_item.plugin_dir_name = plugin_dir.stem
                addon_item.description = plugin_info.get("description", "")
        else:
            try:
                plugin = importlib.import_module(".plugins." + plugin_dir.stem, uniloader_folder_name)
                plugin_info: PluginInfo = plugin.plugin_info
            except Exception as e:
                print(f"Failed to load {plugin_dir.stem} due to {e}:")
                traceback.print_exc()
                continue
            addon_item = registered_addons.add()
            addon_item.name = plugin_info["name"]
            addon_item.id = plugin_info["id"]
            addon_item.version = "{}.{}.{}".format(*plugin_info["version"])
            addon_item.plugin_dir_name = plugin_dir.stem
            addon_item.description = plugin_info.get("description", "")
            addon_item.enabled = False


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


class UniLoader_MT_GroupMenuTemplate(bpy.types.Menu):
    bl_label = "TEMPLATE"
    bl_idname = "IMPORT_MT_group_template"

    operators: list[tuple[str, str]]

    def draw(self, context):
        layout = self.layout
        for operator_idname, operator_desc in self.operators:
            layout.operator(operator_idname, text=operator_desc)


class UniLoader_OT_InstalPlugin(Operator):
    """Install plugin"""
    bl_idname = "uniloader.install_plugin"
    bl_label = "Install UniLoader plugin"
    bl_options = {'UNDO'}

    filepath: StringProperty(
        subtype='FILE_PATH',
    )
    filter_glob: StringProperty(default="*.zip", options={'HIDDEN'})

    def execute(self, context):
        with ZipFile(self.filepath, "r") as f:
            print(f"Installing {Path(self.filepath).stem} addon to {plugins_dir}")
            f.extractall(plugins_dir)
        _scan_plugins()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class UniLoader_OT_InstallGitPlugin(Operator):
    """Install plugin"""
    bl_idname = "uniloader.install_plugin_git"
    bl_label = "Install UniLoader plugin"
    bl_options = {'UNDO'}

    github_url: bpy.props.StringProperty(
        name="GitHub URL",
        description="Enter the URL of the GitHub repository",
    )

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        layout.label(text="Github link")
        layout.prop(self, "github_url")
        layout.separator()

    def execute(self, context):
        if not self.github_url:
            self.report({'ERROR'}, "GitHub URL is empty.")
            return {'CANCELLED'}

        addon_prefs = bpy.context.preferences.addons[__package__].preferences
        registered_addons = addon_prefs.addons
        scheme, netloc, path, params, query, fragment = urllib.parse.urlparse(self.github_url.strip().rstrip())
        if netloc != "github.com":
            self.report({'ERROR'}, "Only installing from github is supported.")
            return {"CANCELLED"}
        *_, user, repo = Path(path).parts

        tags_resp = requests.get(f"https://api.github.com/repos/{user}/{repo}/tags")
        if tags_resp.status_code != 200:
            self.report({'ERROR'}, "Failed to get repo tags.")
            return {"CANCELLED"}

        existing_addon_info = None
        for addon in registered_addons:
            if addon.id == repo:
                existing_addon_info = existing_addon_info

        tags = tags_resp.json()
        if not tags:
            self.report({'ERROR'}, f"No tags found for {user}/{repo}.")
            return {"CANCELLED"}

        chosen_tag = tags[0]
        if existing_addon_info is not None:
            current_version = tuple(map(int, existing_addon_info.version.split(".")))
            chosen_version = tuple(map(int, chosen_tag["name"].split(".")))
            if current_version >= chosen_version:
                self.report({'INFO'}, "Newer or same version is already installed.")
                return {"CANCELLED"}

        zip_resp = requests.get(chosen_tag["zipball_url"])
        if zip_resp.status_code != 200:
            self.report({'ERROR'}, "Failed to download zip")
            return {"CANCELLED"}
        sha = chosen_tag["commit"]["sha"][:7]

        def extract_and_rename(zip_data, extract_to, rename_from, rename_to):
            with ZipFile(zip_data, 'r') as zip_ref:
                for member in zip_ref.infolist():
                    if member.file_size == 0:
                        continue
                    if member.filename.startswith(rename_from):
                        renamed_file = member.filename.replace(rename_from, rename_to, 1)
                        target_path = Path(extract_to) / renamed_file
                        source = zip_ref.open(member)
                        os.makedirs(target_path.parent, exist_ok=True)
                        target = open(target_path, "wb")
                        with source, target:
                            shutil.copyfileobj(source, target)
                    else:
                        # If the file/folder is not the one we want to rename, extract as is
                        zip_ref.extract(member, extract_to)

        extract_and_rename(BytesIO(zip_resp.content), plugins_dir, f"{user}-{repo}-{sha}", repo)
        _scan_plugins()
        return {'FINISHED'}

    def invoke(self, context, event):
        width = 400 * bpy.context.preferences.system.pixel_size
        status = context.window_manager.invoke_props_dialog(self,
                                                            width=int(width))
        return status


class UniLoader_OT_DeletePlugin(bpy.types.Operator):
    """Delete the selected plugin"""
    bl_idname = "uniloader.delete_plugin"
    bl_label = "Delete Selected Plugin"

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[__package__].preferences
        return prefs.selected_addon_index < len(prefs.addons)

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        index = prefs.selected_addon_index
        plugin_to_remove = prefs.addons[index]
        _delete_plugin(plugin_to_remove.plugin_dir_name)
        prefs.addons.remove(index)
        prefs.selected_addon_index = min(max(0, index - 1), len(prefs.addons) - 1)
        return {'FINISHED'}


class UniLoader_OT_RefreshPlugins(Operator):
    """Refresh plugins"""
    bl_idname = "uniloader.refresh_plugins"
    bl_label = "Refresh installed UniLoader plugins"
    bl_options = {'UNDO'}

    def execute(self, context):
        _scan_plugins()
        return {"FINISHED"}


class UniLoader_MT_Menu(bpy.types.Menu):
    bl_label = "UniLoader plugins"
    bl_idname = "uniloader.menu"

    def draw(self, context):
        layout = self.layout
        if PLUGINS:
            for module, menu, _ in PLUGINS.values():
                layout.menu(menu.bl_idname, text=menu.bl_label)
        else:
            layout.label(text="No plugins installed/enabled")


def update_addon_state(self, context):
    """Callback to enable/disable the addon."""
    if self.enabled:
        if self.plugin_dir_name not in PLUGINS and not _load_plugin(self.plugin_dir_name):
            self.enabled = False
            return
    else:
        if self.plugin_dir_name in PLUGINS:
            _unload_plugin(self.plugin_dir_name)
    print(f"Addon {self.name} enabled: {self.enabled}")


class AddonListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list of addons."""
    name: bpy.props.StringProperty(
        name="Name",
        description="Name of the addon"
    )
    plugin_dir_name: bpy.props.StringProperty(
        name="Internal name"
    )
    id: bpy.props.StringProperty(
        name="Internal id"
    )
    version: bpy.props.StringProperty(
        name="Internal version"
    )
    description: bpy.props.StringProperty(
        name="Description",
        description="Description of the addon"
    )
    enabled: bpy.props.BoolProperty(
        name="Enabled",
        description="Whether the addon is enabled or not",
        update=update_addon_state
    )


class UniLoader_UL_pluginlist(bpy.types.UIList):
    """Custom UIList to display more properties of AddonListItem."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        split = row.split(factor=0.15)
        row = split.row()
        row.prop(item, "enabled", emboss=False, icon_only=True,
                 icon='CHECKBOX_HLT' if item.enabled else 'CHECKBOX_DEHLT')
        row.label(text=item.name)

        split = split.split(factor=0.05)
        split.label(text=f"{item.version}")
        split = split.split(factor=0.3)
        row = split.row()
        row.label(text="Path: " + item.plugin_dir_name, icon='FILE_FOLDER')

        sub = split.row()
        sub.label(icon='INFO', text=item.description)


class UniLoaderAddonPreferences(AddonPreferences):
    bl_idname = __package__

    addons: bpy.props.CollectionProperty(type=AddonListItem)
    selected_addon_index: bpy.props.IntProperty()

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.template_list("UniLoader_UL_pluginlist", "addons", self, "addons", self, "selected_addon_index")

        row = layout.row()
        install_split = row.box()
        install_split.operator(UniLoader_OT_InstalPlugin.bl_idname, text="Install plugin")
        install_split.operator(UniLoader_OT_InstallGitPlugin.bl_idname, text="Install plugin from GitHub")
        row.operator(UniLoader_OT_RefreshPlugins.bl_idname, text="Refresh plugins")
        row.operator("uniloader.delete_plugin", text="Delete plugin")


CLASSES = [UniLoader_MT_Menu, UniLoader_OT_InstalPlugin, UniLoader_OT_InstallGitPlugin,
           UniLoader_OT_RefreshPlugins, AddonListItem,
           UniLoader_UL_pluginlist, UniLoaderAddonPreferences,
           UniLoader_OT_DeletePlugin, ]
register_, unregister_ = bpy.utils.register_classes_factory(CLASSES)


def menu_import(self, context):
    self.layout.menu(UniLoader_MT_Menu.bl_idname)


def register():
    register_()
    bpy.types.TOPBAR_MT_file_import.append(menu_import)
    _scan_plugins()


def unregister():
    unregister_()
    for _, menu, operators in PLUGINS.values():
        for _, operator in operators:
            bpy.utils.unregister_class(operator)
        bpy.utils.unregister_class(menu)
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
