import ctypes
import platform
from ctypes import cdll
from pathlib import Path
from typing import Optional

_platform_info = platform.uname()
_lib_path: Optional[Path] = Path(__file__).parent
if _platform_info.system == "Windows":
    _zstd_lib_path = _lib_path / "libzstd.dll"
    _lz4_lib_path = _lib_path / "msys-lz4-1.dll"

# elif _platform_info.system == 'Linux':
#     _lib_path /= "libTextureDecoder.so"
else:
    raise NotImplementedError(f'System {_platform_info} not supported')

_zstd_lib = cdll.LoadLibrary(_zstd_lib_path.as_posix())

# size_t ZSTD_decompress( void* dst, size_t dstCapacity, const void* src, size_t compressedSize);
_zstd_lib.ZSTD_decompress.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
_zstd_lib.ZSTD_decompress.restype = ctypes.c_size_t


def zstd_decompress(compressed_data: bytes, decompressed_size: int):
    decompressed_data = bytes(decompressed_size)
    actual_decompressed_size = _zstd_lib.ZSTD_decompress(decompressed_data, decompressed_size, compressed_data,
                                                         len(compressed_data))
    return decompressed_data[:actual_decompressed_size]
