from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import Callable

import numpy as np


class VertexAttributeType(Enum):
    """Represents the type of vertex attribute."""
    Float = (np.float32, (1,))
    Vector2 = (np.float32, (2,))
    Vector3 = (np.float32, (3,))
    Vector4 = (np.float32, (4,))
    UByte4 = (np.uint8, (4,))
    Matrix4x4 = (np.float32, (4, 4))
    Custom = (np.void, (0,))


# noinspection PyPep8Naming
class _MetaVertexAttributeSemantic(type):
    """Meta class for VertexAttributeSemantic to provide quick constructors for common semantics."""

    @property
    def Position(cls):
        return VertexAttributeSemantic("POSITION")

    @property
    def Normal(cls):
        return VertexAttributeSemantic("NORMAL")

    @property
    def Tangent(cls):
        return VertexAttributeSemantic("TANGENT")

    @classmethod
    def Color(cls, index: int):
        return VertexAttributeSemantic("COLOR", index)

    @property
    def Color0(cls):
        return cls.Color(0)

    @property
    def Color1(cls):
        return cls.Color(1)

    @property
    def Color2(cls):
        return cls.Color(2)

    @property
    def Color3(cls):
        return cls.Color(3)

    @classmethod
    def UV(cls, index: int):
        return VertexAttributeSemantic("UV", index)

    @property
    def UV0(cls):
        return cls.UV(0)

    @property
    def UV1(cls):
        return cls.UV(1)

    @property
    def UV2(cls):
        return cls.UV(2)

    @property
    def UV3(cls):
        return cls.UV(3)

    @classmethod
    def BoneIndices(cls, index: int):
        return VertexAttributeSemantic("BONE_INDICES", index)

    @property
    def BoneIndices0(cls):
        return cls.BoneIndices(0)

    @property
    def BoneIndices1(cls):
        return cls.BoneIndices(1)

    @classmethod
    def BoneWeights(cls, index: int):
        return VertexAttributeSemantic("BONE_WEIGHT", index)

    @property
    def BoneWeights0(cls):
        return cls.BoneWeights(0)

    @property
    def BoneWeights1(cls):
        return cls.BoneWeights(1)


@dataclass(slots=True)
class VertexAttributeSemantic(metaclass=_MetaVertexAttributeSemantic):
    """Represents a semantic for a vertex attribute."""
    name: str
    index: int = field(default=-1)

    def id(self):
        """Returns the ID of the semantic."""
        return self.name if self.index < 0 else f"{self.name}{self.index}"

    def __repr__(self):
        return self.id()


@dataclass(slots=True)
class VertexAttribute:
    """Represents a vertex attribute in a vertex buffer."""
    semantic: VertexAttributeSemantic
    type: VertexAttributeType
    inner_type: VertexAttributeType | None = field(default=None)  # Optional, defaults to same value as type
    converter: Callable[[np.ndarray], np.ndarray] | None = field(default=None)  # Must be present for Custom inner type
    size: int | None = field(default=None)  # Must be present for Custom inner type or when type!=inner_type
    data: np.ndarray = field(default=None)  # Used only for non-interleaved vertex data

    def __post_init__(self):
        if self.inner_type is None:
            self.inner_type = self.type

        if self.inner_type == VertexAttributeType.Custom:
            if self.converter is None or self.size is None:
                raise ValueError("Custom inner type requires converter and size")
        elif self.type != self.inner_type and self.converter is None:
            raise ValueError("Converter must be None when type != inner_type")


@dataclass
class VertexBuffer:
    """Represents a vertex buffer."""
    attributes: list[VertexAttribute] = field(default_factory=list)
    interleaved: bool = field(default=True)
    data: bytes | None = field(
        default=None)  # Optional storage, will be used for interleaved vertex data if no argument for read_vertices provided

    def add_attribute(self, semantic: VertexAttributeSemantic,
                      type: VertexAttributeType,
                      inner_type: VertexAttributeType | None = None,
                      converter: Callable[[np.ndarray], np.ndarray] | None = None,
                      size: int | None = None):
        """Adds an attribute to the vertex buffer."""
        self.attributes.append(VertexAttribute(semantic, type, inner_type, converter, size))

    def has_attribute(self, semantic: VertexAttributeSemantic):
        """Checks if the vertex buffer has the specified attribute."""
        return any(attr.semantic == semantic for attr in self.attributes)

    def read_vertices(self, count: int, data: bytes | None = None):
        """Reads vertex data from the buffer or from attributes own buffers for non-interleaved vertex data."""
        if data is None and self.data is None:
            raise ValueError("No data provided to read from: argument data is None and self.data is None")
        data = data or self.data
        if self.stride * count != len(data):
            raise ValueError(f"Data length {len(data)} does not match expected size {self.stride} * {count}")
        output_buffer = np.empty(count, dtype=self.dtype)
        if self.interleaved:
            if all(attr.type == attr.inner_type for attr in self.attributes):
                return np.frombuffer(data, dtype=self.dtype)
            raw_data = np.frombuffer(data, dtype=self._inner_dtype)
            for attribute in self.attributes:
                if attribute.type != attribute.inner_type:
                    if attribute.converter is None:
                        raise ValueError(f"Converter required for attribute {attribute.semantic}")

                attribute_data = raw_data[attribute.semantic.name]
                if attribute.converter is not None:
                    output_buffer[attribute.semantic.name] = attribute.converter(attribute_data)
                else:
                    output_buffer[attribute.semantic.name] = attribute_data
        else:
            for attribute in self.attributes:
                if attribute.data is None:
                    raise ValueError(f"Attribute {attribute.semantic} has no data for non-interleaved vertex buffer")
                if attribute.type != attribute.inner_type:
                    if attribute.converter is None:
                        raise ValueError(f"Converter required for attribute {attribute.semantic}")

                attribute_data = np.frombuffer(data, dtype=output_buffer[attribute.semantic.name].dtype)
                if attribute.converter is not None:
                    output_buffer[attribute.semantic.name] = attribute.converter(attribute_data)
                else:
                    output_buffer[attribute.semantic.name] = attribute_data
        return output_buffer

    def __post_init__(self):
        if not self.interleaved:
            for attribute in self.attributes:
                if attribute.data is None:
                    raise ValueError("Data must be provided for non-interleaved vertex buffer")

    @cached_property
    def stride(self):
        return sum(
            attr.size if attr.inner_type == VertexAttributeType.Custom else
            np.prod(attr.type.value[1]) * np.dtype(attr.type.value[0]).itemsize
            for attr in self.attributes
        )

    @property
    def dtype(self):
        """Returns the data type of the vertex buffer."""
        members = []
        for attribute in self.attributes:
            members.append((attribute.semantic.id(), *attribute.type.value))
        return np.dtype(members)

    @property
    def _inner_dtype(self):
        """Returns the inner data type of the vertex buffer."""
        members = []
        for attribute in self.attributes:
            members.append((attribute.semantic.id(), *attribute.inner_type.value))
        return np.dtype(members)


if __name__ == '__main__':
    buff = VertexBuffer([
        VertexAttribute(VertexAttributeSemantic.Position, VertexAttributeType.Vector3, VertexAttributeType.Vector3),
        VertexAttribute(VertexAttributeSemantic.Normal, VertexAttributeType.Vector3, VertexAttributeType.Custom,
                        lambda a: a, 4),
        VertexAttribute(VertexAttributeSemantic.Tangent, VertexAttributeType.Vector3, VertexAttributeType.Vector3),
    ])

    print(buff)
    print(buff.stride)
