from ctypes import c_int32, c_char_p, c_void_p, POINTER, c_uint32, HRESULT

from UniLoader.experimental.guid import GUID
from UniLoader.experimental.winapi_interface import Interface


class IUnknown(Interface):
    iid: GUID = GUID.of("4605c4cb-2019-492a-ada4-65f20bb7d67f")

    def _register_functions(self):
        self._add_virtual_function(0, "QueryInterface", c_int32, [c_char_p, POINTER(c_void_p)])
        self._add_virtual_function(1, "AddRef", HRESULT, [])
        self._add_virtual_function(2, "Release", HRESULT, [])

    def __del__(self):
        print("Del called for", self.__class__.__name__)
        if self.is_valid():
            self._vcall("Release")
