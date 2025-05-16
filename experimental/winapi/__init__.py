from typing import TypeVar
from uuid import UUID

from ctypes import CDLL, c_char_p, c_void_p, c_int32, HRESULT, c_size_t, c_uint32, POINTER, byref

from .iunknown import IUnknown
from .d3dcompiler.interfaces import ID3DBlob

IUnknownT = TypeVar("IUnknownT", bound=IUnknown)


class DXCompiler(CDLL):

    def __init__(self, name: str | None):
        super().__init__(name)
        self.DxcCreateInstance.argtypes = [c_char_p, c_char_p, POINTER(c_void_p)]
        self.DxcCreateInstance.restype = c_int32

    def create_instance(self, clsid: UUID, iface_type: type[IUnknownT]) -> IUnknownT:
        instance_ptr = iface_type()
        res = self.DxcCreateInstance(clsid.bytes_le, iface_type.iid.bytes_le, instance_ptr)
        if res != 0:
            raise RuntimeError(f"Failed to create instance: {res:#x}")
        return instance_ptr


class D3DCompiler(CDLL):

    def __init__(self, name: str | None):
        super().__init__(name)
        self.D3DDisassemble.argtypes = [c_char_p, c_size_t, c_uint32, c_char_p, POINTER(c_void_p)]
        self.D3DDisassemble.restype = HRESULT
        self.D3DReflect.argtypes = [c_char_p, c_size_t, c_char_p, POINTER(c_void_p)]
        self.D3DReflect.restype = HRESULT

    def disassemble(self, source: bytes, flags: int) -> ID3DBlob:
        blob = ID3DBlob()
        res = self.D3DDisassemble(source, len(source), flags, c_char_p(0), byref(blob))
        if res != 0:
            raise RuntimeError(f"Failed to create instance: {res:#x}")
        return blob

    def reflect(self, source: bytes, iface_type:type[IUnknownT]) -> IUnknownT:
        reflector = iface_type()
        res = self.D3DReflect(source, len(source), iface_type.iid.bytes_le, reflector)
        if res != 0:
            raise RuntimeError(f"Failed to create instance: {res:#x}")
        return reflector