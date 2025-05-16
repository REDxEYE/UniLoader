from ctypes import c_void_p, c_size_t, c_uint32, create_string_buffer, cast, c_char_p, string_at
from enum import IntEnum

from _ctypes import Structure


class DxcBuffer(Structure):
    _fields_ = [
        ("Ptr", c_void_p),
        ("Size", c_size_t),
        ("Encoding", c_uint32)
    ]

    def __init__(self, data: bytes, encoding: int):
        buf = create_string_buffer(data)
        super().__init__(cast(buf, c_void_p), c_size_t(len(data)), c_uint32(encoding))


class D3D12ShaderVariableDesc(Structure):
    _fields_ = [
        ("_Name", c_size_t),
        ("StartOffset", c_uint32),
        ("Size", c_uint32),
        ("uFlags", c_uint32),
        ("DefaultValue", c_void_p),
        ("StartTexture", c_uint32),
        ("TextureSize", c_uint32),
        ("StartSampler", c_uint32),
        ("SamplerSize", c_uint32),
    ]

    @property
    def name(self):
        if self._Name:
            return string_at(self._Name).decode("utf-8")
        return ""

    @property
    def start_offset(self):
        return self.StartOffset

    @property
    def size(self):
        return self.Size

    @property
    def flags(self):
        return self.uFlags

    @property
    def default_value(self):
        return self.DefaultValue

    @property
    def start_texture(self):
        return self.StartTexture

    @property
    def texture_size(self):
        return self.TextureSize

    @property
    def start_sampler(self):
        return self.StartSampler

    @property
    def sampler_size(self):
        return self.SamplerSize

    def __repr__(self):
        return f"D3D12ShaderVariableDesc(Name={self.name!r}, StartOffset={self.start_offset}, Size={self.size}, uFlags={self.flags})"

class D3D_CBUFFER_TYPE(IntEnum):
    CBUFFER = 0
    TBUFFER = 1
    INTERFACE_POINTERS = 2
    RESOURCE_BIND_INFO = 3

class D3D12ShaderBufferDesc(Structure):
    _fields_ = [
        ("_Name", c_size_t),
        ("Type", c_uint32),
        ("Variables", c_uint32),
        ("Size", c_uint32),
        ("Flags", c_uint32)
    ]

    @property
    def name(self):
        if self._Name:
            return string_at(self._Name).decode("utf-8")
        return ""
    @property
    def type(self):
        return D3D_CBUFFER_TYPE(self.Type)

    @property
    def variables(self):
        return self.Variables

    @property
    def size(self):
        return self.Size

    @property
    def flags(self):
        return self.Flags

    def __repr__(self):
        return f"D3D12ShaderBufferDesc(Name={self.name!r}, Type={self.type}, Variables={self.variables}, Size={self.size}, Flags={self.flags})"


class D3DShaderVariableClass(IntEnum):
    SCALAR = 0
    VECTOR = 1
    MATRIX_ROWS = 2
    MATRIX_COLUMNS = 3
    OBJECT = 4
    STRUCT = 5
    INTERFACE_CLASS = 6
    INTERFACE_POINTER = 7


class D3DShaderVariableType(IntEnum):
    VOID = 0
    BOOL = 1
    INT = 2
    FLOAT = 3
    STRING = 4
    TEXTURE = 5
    TEXTURE1D = 6
    TEXTURE2D = 7
    TEXTURE3D = 8
    TEXTURECUBE = 9
    SAMPLER = 10
    SAMPLER1D = 11
    SAMPLER2D = 12
    SAMPLER3D = 13
    SAMPLERCUBE = 14
    PIXELSHADER = 15
    VERTEXSHADER = 16
    PIXELFRAGMENT = 17
    VERTEXFRAGMENT = 18
    UINT = 19
    UINT8 = 20
    GEOMETRYSHADER = 21
    RASTERIZER = 22
    DEPTHSTENCIL = 23
    BLEND = 24
    BUFFER = 25
    CBUFFER = 26
    TBUFFER = 27
    TEXTURE1DARRAY = 28
    TEXTURE2DARRAY = 29
    RENDERTARGETVIEW = 30
    DEPTHSTENCILVIEW = 31
    TEXTURE2DMS = 32
    TEXTURE2DMSARRAY = 33
    TEXTURECUBEARRAY = 34
    HULLSHADER = 35
    DOMAINSHADER = 36
    INTERFACE_POINTER = 37
    COMPUTESHADER = 38
    DOUBLE = 39
    RWTEXTURE1D = 40
    RWTEXTURE1DARRAY = 41
    RWTEXTURE2D = 42
    RWTEXTURE2DARRAY = 43
    RWTEXTURE3D = 44
    RWBUFFER = 45
    BYTEADDRESS_BUFFER = 46
    RWBYTEADDRESS_BUFFER = 47
    STRUCTURED_BUFFER = 48
    RWSTRUCTURED_BUFFER = 49
    APPEND_STRUCTURED_BUFFER = 50
    CONSUME_STRUCTURED_BUFFER = 51
    MIN8FLOAT = 52
    MIN10FLOAT = 53
    MIN16FLOAT = 54
    MIN12INT = 55
    MIN16INT = 56
    MIN16UINT = 57


class D3D12ShaderTypeDesc(Structure):
    _fields_ = [
        ("Class", c_uint32),
        ("Type", c_uint32),
        ("Rows", c_uint32),
        ("Columns", c_uint32),
        ("Elements", c_uint32),
        ("Members", c_uint32),
        ("Offset", c_uint32),
        ("_Name", c_size_t),
    ]

    @property
    def name(self):
        if self._Name:
            return string_at(self._Name).decode("utf-8")
        return ""

    @property
    def class_type(self):
        return D3DShaderVariableClass(self.Class)

    @property
    def type(self):
        return D3DShaderVariableType(self.Type)

    def __repr__(self):
        return f"D3D12ShaderTypeDesc(Class={self.class_type!r}, Type={self.type!r}, Rows={self.Rows}, Columns={self.Columns}, Elements={self.Elements}, Members={self.Members}, Name={self.name!r})"


class D3DShaderInputType(IntEnum):
    CBUFFER = 0
    TBUFFER = 1
    TEXTURE = 2
    SAMPLER = 3
    UAV_RWTYPED = 4
    STRUCTURED = 5
    UAV_RWSTRUCTURED = 6
    BYTEADDRESS = 7
    UAV_RWBYTEADDRESS = 8
    UAV_APPEND_STRUCTURED = 9
    UAV_CONSUME_STRUCTURED = 10
    UAV_RWSTRUCTURED_WITH_COUNTER = 11
    RTACCELERATIONSTRUCTURE = 12
    UAV_FEEDBACKTEXTURE = 13


class D3DResourceReturnType(IntEnum):
    UNORM = 1
    SNORM = 2
    SINT = 3
    UINT = 4
    FLOAT = 5
    MIXED = 6
    DOUBLE = 7
    CONTINUED = 8


class D3D12ShaderInputBindDesc(Structure):
    _fields_ = [
        ("_Name", c_char_p),
        ("_Type", c_uint32),
        ("BindPoint", c_uint32),
        ("BindCount", c_uint32),
        ("uFlags", c_uint32),
        ("_ReturnType", c_uint32),
        ("Dimension", c_uint32),
        ("NumSamples", c_uint32),
        ("Space", c_uint32)
    ]

    @property
    def name(self):
        if self._Name:
            return string_at(self._Name).decode("utf-8")
        return ""

    @property
    def type(self):
        return D3DShaderInputType(self._Type)

    @property
    def return_type(self):
        return D3DResourceReturnType(self._ReturnType) if self.type == D3DShaderInputType.TEXTURE else None

    def __repr__(self):
        return f"D3D12ShaderInputBindDesc(Name={self.name!r}, Type={self.type!r}, BindPoint={self.BindPoint}, BindCount={self.BindCount}, uFlags={self.uFlags}, ReturnType={self.return_type!r}, Dimension={self.Dimension}, NumSamples={self.NumSamples}, Space={self.Space})"


class D3D12ShaderDesc(Structure):
    _fields_ = [
        ("Version", c_uint32),
        ("_Creator", c_size_t),
        ("Flags", c_uint32),

        ("ConstantBuffers", c_uint32),
        ("BoundResources", c_uint32),
        ("InputParameters", c_uint32),
        ("OutputParameters", c_uint32),

        ("InstructionCount", c_uint32),
        ("TempRegisterCount", c_uint32),
        ("TempArrayCount", c_uint32),
        ("DefCount", c_uint32),
        ("DclCount", c_uint32),
        ("TextureNormalInstructions", c_uint32),
        ("TextureLoadInstructions", c_uint32),
        ("TextureCompInstructions", c_uint32),
        ("TextureBiasInstructions", c_uint32),
        ("TextureGradientInstructions", c_uint32),
        ("FloatInstructionCount", c_uint32),
        ("IntInstructionCount", c_uint32),
        ("UintInstructionCount", c_uint32),
        ("StaticFlowControlCount", c_uint32),
        ("DynamicFlowControlCount", c_uint32),
        ("MacroInstructionCount", c_uint32),
        ("ArrayInstructionCount", c_uint32),
        ("CutInstructionCount", c_uint32),
        ("EmitInstructionCount", c_uint32),
        ("GSOutputTopology", c_uint32),
        ("GSMaxOutputVertexCount", c_uint32),
        ("InputPrimitive", c_uint32),
        ("PatchConstantParameters", c_uint32),
        ("cGSInstanceCount", c_uint32),
        ("cControlPoints", c_uint32),
        ("HSOutputPrimitive", c_uint32),
        ("HSPartitioning", c_uint32),
        ("TessellatorDomain", c_uint32),
        ("cBarrierInstructions", c_uint32),
        ("cInterlockedInstructions", c_uint32),
        ("cTextureStoreInstructions", c_uint32)
    ]

    @property
    def creator(self):
        if self._Creator:
            return string_at(self._Creator).decode("utf-8")
        return ""

    def __repr__(self):
        return f"D3D12ShaderDesc(Version={self.Version}, Creator={self.creator!r}, Flags={self.Flags}, ConstantBuffers={self.ConstantBuffers}, BoundResources={self.BoundResources}, InputParameters={self.InputParameters}, OutputParameters={self.OutputParameters}, InstructionCount={self.InstructionCount}, TempRegisterCount={self.TempRegisterCount}, TempArrayCount={self.TempArrayCount}, DefCount={self.DefCount}, DclCount={self.DclCount}, TextureNormalInstructions={self.TextureNormalInstructions}, TextureLoadInstructions={self.TextureLoadInstructions}, TextureCompInstructions={self.TextureCompInstructions}, TextureBiasInstructions={self.TextureBiasInstructions}, TextureGradientInstructions={self.TextureGradientInstructions}, FloatInstructionCount={self.FloatInstructionCount}, IntInstructionCount={self.IntInstructionCount}, UintInstructionCount={self.UintInstructionCount}, StaticFlowControlCount={self.StaticFlowControlCount}, DynamicFlowControlCount={self.DynamicFlowControlCount}, MacroInstructionCount={self.MacroInstructionCount}, ArrayInstructionCount={self.ArrayInstructionCount}, CutInstructionCount={self.CutInstructionCount}, EmitInstructionCount={self.EmitInstructionCount})"
