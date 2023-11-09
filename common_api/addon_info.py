from typing import TypedDict, Type, Any, Callable

import bpy


class PropertyInfo(TypedDict):
    name: str
    prop_name: str
    bl_type: Type[bpy.types.Property]
    kwargs: dict[str, Any]


class LoaderInfo(TypedDict):
    name: str
    id: str
    exts: tuple[str]
    properties: list[PropertyInfo]
    init_fn: Callable[[], None]
    import_fn: Callable[[Any, str, list], set[str]]


class PluginInfo(TypedDict):
    name: str  # Name shown in plugin list
    id: str  # Must match repo name
    version: tuple[int, int, int]
    description: str
    loaders: list[LoaderInfo]
    init_fn: Callable[[], None]
