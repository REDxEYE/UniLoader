from _ctypes import POINTER, byref
from ctypes import c_uint32, c_char_p, HRESULT

from UniLoader.experimental.guid import GUID
from UniLoader.experimental.winapi.dxcompiler.interfaces import ID3D12ShaderReflection
from UniLoader.experimental.winapi.dxcompiler.structs import DxcBuffer
from UniLoader.experimental.winapi.iunknown import IUnknown


class IDxcUtils(IUnknown):
    iid = GUID.of("4605c4cb-2019-492a-ada4-65f20bb7d67f")

    def _register_functions(self):
        super()._register_functions()
        self._add_virtual_function(13, "CreateReflection", HRESULT,
                                   [POINTER(DxcBuffer), c_char_p, ID3D12ShaderReflection])

    def create_reflection(self, bitcode_blob: bytes):
        buffer = DxcBuffer(bitcode_blob, 0)
        reflection = ID3D12ShaderReflection()
        res = self._vcall("CreateReflection", byref(buffer), ID3D12ShaderReflection.iid.bytes_le, byref(reflection))
        if res != 0:
            raise RuntimeError(f"Failed to create reflection: {res:#x}")
        return reflection
