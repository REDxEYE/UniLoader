from _ctypes import POINTER, byref
from ctypes import c_uint32, c_char_p, cast, HRESULT

from UniLoader.experimental.guid import GUID
from UniLoader.experimental.winapi.dxcompiler.structs import D3D12ShaderTypeDesc, D3D12ShaderVariableDesc, \
    D3D12ShaderBufferDesc, D3D12ShaderInputBindDesc, D3D12ShaderDesc
from UniLoader.experimental.winapi.iunknown import IUnknown
from UniLoader.experimental.winapi_interface import Interface


class ID3D12ShaderReflectionType(Interface):
    iid = GUID.of("e913c351-783d-48ca-a1d1-4f306284ad56")

    def _register_functions(self):
        self._add_virtual_function(0, "GetDesc", HRESULT, [POINTER(D3D12ShaderTypeDesc)])
        self._add_virtual_function(1, "GetMemberTypeByIndex", ID3D12ShaderReflectionType, [c_uint32])
        self._add_virtual_function(2, "GetMemberTypeByName", ID3D12ShaderReflectionType, [c_char_p])
        self._add_virtual_function(3, "GetMemberTypeName", c_char_p, [c_uint32])
        self._add_virtual_function(4, "IsEqual", HRESULT, [ID3D12ShaderReflectionType])
        self._add_virtual_function(5, "GetSubType", ID3D12ShaderReflectionType, [])
        self._add_virtual_function(6, "GetBaseClass", ID3D12ShaderReflectionType, [])
        self._add_virtual_function(7, "GetNumInterfaces", c_uint32, [])
        self._add_virtual_function(8, "GetInterfaceByIndex", ID3D12ShaderReflectionType, [c_uint32])
        self._add_virtual_function(9, "IsOfType", HRESULT, [ID3D12ShaderReflectionType])
        self._add_virtual_function(10, "ImplementsInterface", HRESULT, [ID3D12ShaderReflectionType])

    def get_desc(self)->D3D12ShaderTypeDesc:
        desc = D3D12ShaderTypeDesc()
        res = self._vcall("GetDesc", byref(desc))
        if res != 0:
            raise RuntimeError(f"Failed to get type description: {res:#x}")
        return desc

    def get_member_type_by_index(self, index: int) -> 'ID3D12ShaderReflectionType':
        type_ptr = self._vcall("GetMemberTypeByIndex", index)
        if type_ptr is None:
            raise RuntimeError(f"Failed to get member type by index: {index}")
        return type_ptr

    def get_member_type_by_name(self, name: str) -> 'ID3D12ShaderReflectionType':
        type_ptr = self._vcall("GetMemberTypeByName", name.encode("utf-8"))
        if type_ptr is None:
            raise RuntimeError(f"Failed to get member type by name: {name}")
        return type_ptr

    def get_member_type_name(self, index: int) -> str:
        name_ptr = self._vcall("GetMemberTypeName", index)
        if name_ptr is None:
            raise RuntimeError(f"Failed to get member name by index: {index}")
        return cast(name_ptr, c_char_p).value.decode("utf-8")

    def is_equal(self, other: 'ID3D12ShaderReflectionType') -> bool:
        res = self._vcall("IsEqual", other)
        if res == 0:
            return False
        elif res == 1:
            return True
        else:
            raise RuntimeError(f"Failed to compare types: {res:#x}")

    def get_sub_type(self) -> 'ID3D12ShaderReflectionType':
        sub_type_ptr: ID3D12ShaderReflectionType | None = self._vcall("GetSubType")
        return sub_type_ptr

    def get_base_class(self) -> 'ID3D12ShaderReflectionType':
        base_class_ptr: ID3D12ShaderReflectionType | None = self._vcall("GetBaseClass")
        return base_class_ptr

    def get_num_interfaces(self) -> int:
        return self._vcall("GetNumInterfaces")

    def get_interface_by_index(self, index: int) -> 'ID3D12ShaderReflectionType':
        interface_ptr = self._vcall("GetInterfaceByIndex", index)
        if interface_ptr is None:
            raise RuntimeError(f"Failed to get interface by index: {index}")
        return interface_ptr

    def is_of_type(self, other: 'ID3D12ShaderReflectionType') -> bool:
        res = self._vcall("IsOfType", other)
        if res == 0:
            return False
        elif res == 1:
            return True
        else:
            raise RuntimeError(f"Failed to check if type is of type: {res:#x}")

    def implements_interface(self, other: 'ID3D12ShaderReflectionType') -> bool:
        res = self._vcall("ImplementsInterface", other)
        if res == 0:
            return False
        elif res == 1:
            return True
        else:
            raise RuntimeError(f"Failed to check if type implements interface: {res:#x}")

    @property
    def members(self):
        members = []
        for i in range(self.get_desc().Members):
            members.append(self.get_member_type_by_index(i))
        return members

    def __repr__(self):
        if self.is_valid():
            desc = self.get_desc()
            return f"ID3D12ShaderReflectionType(Name={desc.name!r}, class={desc.class_type!r}, type={desc.type!r})"
        return "ID3D12ShaderReflectionType(Invalid Pointer)"

class ID3D12ShaderReflectionVariable(Interface):
    iid = GUID.of("8337a8a6-a216-444a-b2f4-314733a73aea")

    def _register_functions(self):
        self._add_virtual_function(0, "GetDesc", HRESULT, [POINTER(D3D12ShaderVariableDesc)])
        self._add_virtual_function(1, "GetType", ID3D12ShaderReflectionType, [])
        self._add_virtual_function(2, "GetBuffer", ID3D12ShaderReflectionConstantBuffer, [])
        self._add_virtual_function(3, "GetInterfaceSlot", c_uint32, [c_uint32])

    def get_desc(self) -> D3D12ShaderVariableDesc:
        desc = D3D12ShaderVariableDesc()
        res = self._vcall("GetDesc", byref(desc))
        if res != 0:
            raise RuntimeError(f"Failed to get variable description: {res:#x}")
        return desc

    def get_type(self) -> ID3D12ShaderReflectionType:
        type_ptr = self._vcall("GetType")
        if type_ptr is None:
            raise RuntimeError("Failed to get type pointer")
        return type_ptr

    def get_buffer(self) -> 'ID3D12ShaderReflectionConstantBuffer':
        buffer_ptr = self._vcall("GetBuffer")
        if buffer_ptr is None:
            raise RuntimeError("Failed to get buffer pointer")
        return buffer_ptr

    def get_interface_slot(self, index: int) -> int:
        slot = self._vcall("GetInterfaceSlot", index)
        if slot is None:
            raise RuntimeError(f"Failed to get interface slot: {index}")
        return slot

    @property
    def name(self):
        desc = self.get_desc()
        return desc.name or "Anonymous"

    @property
    def type(self):
        return self.get_type()

    def __repr__(self):
        return f"ID3D12ShaderReflectionVariable(Name={self.name!r})"


class ID3D12ShaderReflectionConstantBuffer(Interface):
    iid = GUID.of("c59598b4-48b3-4869-b9b1-b1618b14a8b7")

    def _register_functions(self):
        self._add_virtual_function(0, "GetDesc", HRESULT, [POINTER(D3D12ShaderBufferDesc)])
        self._add_virtual_function(1, "GetVariableByIndex", ID3D12ShaderReflectionVariable, [c_uint32])
        self._add_virtual_function(2, "GetVariableByName", ID3D12ShaderReflectionVariable, [c_char_p])

    def get_desc(self):
        desc = D3D12ShaderBufferDesc()
        res = self._vcall("GetDesc", byref(desc))
        if res != 0:
            raise RuntimeError(f"Failed to get constant buffer description: {res:#x}")
        return desc

    def get_variable_by_index(self, index: int) -> ID3D12ShaderReflectionVariable:
        variable = self._vcall("GetVariableByIndex", index)
        if variable is None:
            raise RuntimeError(f"Failed to get variable by index: {index}")
        return variable

    def get_variable_by_name(self, name: str) -> ID3D12ShaderReflectionVariable:
        variable = self._vcall("GetVariableByName", name.encode("utf-8"))
        if variable is None:
            raise RuntimeError(f"Failed to get variable by name: {name}")
        return variable

    @property
    def name(self):
        desc = self.get_desc()
        return desc.name

    @property
    def variables(self):
        variables = []
        for i in range(self.get_desc().Variables):
            variables.append(self.get_variable_by_index(i))
        return variables

    def __repr__(self):
        return f"ID3D12ShaderReflectionConstantBuffer(Name={self.name!r})"


class ID3D12ShaderReflection(IUnknown):
    iid = GUID.of("5a58797d-a72c-478d-8ba2-efc6b0efe88e")

    def _register_functions(self):
        super()._register_functions()
        self._add_virtual_function(3, "GetDesc", HRESULT, [POINTER(D3D12ShaderDesc)])
        self._add_virtual_function(4, "GetConstantBufferByIndex", ID3D12ShaderReflectionConstantBuffer, [c_uint32])
        self._add_virtual_function(6, "GetResourceBindingDesc", HRESULT, [c_uint32, POINTER(D3D12ShaderInputBindDesc)])

    def get_desc(self) -> D3D12ShaderDesc:
        desc = D3D12ShaderDesc()
        res = self._vcall("GetDesc", byref(desc))
        if res != 0:
            raise RuntimeError(f"Failed to get shader description: {res:#x}")
        return desc

    def get_constant_buffer_by_index(self, index: int) -> ID3D12ShaderReflectionConstantBuffer:
        ptr = self._vcall("GetConstantBufferByIndex", index)
        if ptr is None:
            raise RuntimeError(f"Failed to get constant buffer by index: {index}")
        return ptr

    def get_resource_binding_desc(self, index: int) -> D3D12ShaderInputBindDesc:
        desc = D3D12ShaderInputBindDesc()
        res = self._vcall("GetResourceBindingDesc", index, byref(desc))
        if res != 0:
            raise RuntimeError(f"Failed to get resource binding description: {res:#x}")
        return desc

    @property
    def constant_buffers(self):
        buffers = []
        for i in range(self.get_desc().ConstantBuffers):
            buffers.append(self.get_constant_buffer_by_index(i))
        return buffers

    @property
    def input_parameters(self):
        inputs = []
        for i in range(self.get_desc().InputParameters):
            inputs.append(self.get_resource_binding_desc(i))
        return inputs

    @property
    def bindings(self):
        inputs = []
        for i in range(self.get_desc().BoundResources):
            inputs.append(self.get_resource_binding_desc(i))
        return inputs