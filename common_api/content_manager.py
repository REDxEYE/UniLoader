import abc
from typing import Iterable

from UniLoader.common_api import Buffer


class ContentProvider(abc.ABC):
    @abc.abstractmethod
    def exists(self, filepath: str) -> bool:
        raise NotImplementedError("Exists method not implemented")

    @abc.abstractmethod
    def get(self, filepath: str) -> Buffer:
        raise NotImplementedError("Get method not implemented")

    @abc.abstractmethod
    def glob(self, pattern: str) -> Iterable[tuple[str, Buffer]]:
        raise NotImplementedError("Glob method not implemented")

    @abc.abstractmethod
    def name(self):
        raise NotImplementedError("Name method not implemented")


class ContentManager:
    def __init__(self):
        self.mounts: list[ContentProvider] = []

    def get(self, filepath: str) -> Buffer | None:
        print("[*] Searching for:", filepath)
        for mount in self.mounts:
            if mount.exists(filepath):
                return mount.get(filepath)
        return None

    def glob(self, pattern: str) -> Iterable[tuple[str, Buffer]]:
        for mount in self.mounts:
            for name_file in mount.glob(pattern):
                yield name_file

    def glob_first(self, pattern: str) -> tuple[str, Buffer] | None:
        for mount in self.mounts:
            for name_file in mount.glob(pattern):
                return name_file
        return None

    def mount(self, provider: ContentProvider):
        if provider in self.mounts:
            raise ValueError("Provider already mounted")
        print("Mounted:", provider.name())
        self.mounts.append(provider)

    def unmount(self, provider: ContentProvider):
        if provider not in self.mounts:
            raise ValueError("Provider not mounted")
        print("Unmounted:", provider.name())
        self.mounts.remove(provider)