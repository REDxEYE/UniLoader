import os
import platform

from UniLoader.common_api.tiny_path import TinyPath

def _pop_path_back(path: TinyPath):
    if len(path.parts) > 1:
        return TinyPath(os.sep.join(path.parts[1:]))
    else:
        return path


def _pop_path_front(path: TinyPath):
    if len(path.parts) > 1:
        return TinyPath(os.sep.join(path.parts[:-1]))
    else:
        return path


def find_in_parents(current_path, file_to_find) -> TinyPath | None:
    current_path = TinyPath(current_path).absolute()
    file_to_find = TinyPath(file_to_find)

    for _ in range(len(current_path.parts) - 1):
        second_part = file_to_find
        for _ in range(len(file_to_find.parts)):
            new_path = rebuild_path_for_case_sensetive_fs(current_path / second_part)
            if new_path.exists():
                return new_path

            second_part = _pop_path_back(second_part)
        current_path = _pop_path_front(current_path)
    return None


def rebuild_path_for_case_sensetive_fs(path: TinyPath):
    if platform.system() == "Windows" or path.exists():  # Shortcut for windows
        return path
    if len(path.parts) < 3:
        return path
    root, *parts, fname = path.parts

    new_path = TinyPath(root)
    for part in parts:
        for dir_name in new_path.iterdir():
            if dir_name.is_file():
                continue
            if dir_name.name.lower() == part.lower():
                new_path = dir_name
                break
    for file_name in new_path.iterdir():
        if file_name.is_file() and file_name.name.lower() == fname.lower():
            return file_name
    return path
