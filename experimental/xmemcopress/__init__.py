from pathlib import Path

from ctypes import WinDLL, c_void_p, c_int32, c_char_p, POINTER, byref, pointer, create_string_buffer, c_uint32, \
    Structure, c_uint64


class XMEMCODEC_PARAMETERS_LZX(Structure):
    _fields_ = [
        ("Flags", c_uint32),
        ("WindowSize", c_uint32),
        ("CompressionPartitionSize", c_uint32),
        ("unk0", c_uint32),
        ("unk1", c_uint32),
        ("unk2", c_uint32),
    ]


class XCompressLib:
    _dll = WinDLL((Path(__file__).parent / "xcompress64.dll").as_posix())

    xmem_create_decompression_context = _dll.XMemCreateDecompressionContext
    xmem_create_decompression_context.argtypes = [c_uint32, POINTER(XMEMCODEC_PARAMETERS_LZX), c_int32,
                                                  POINTER(c_void_p)
                                                  ]
    xmem_create_decompression_context.restype = c_int32

    xmem_decompress = _dll.XMemDecompress
    xmem_decompress.argtypes = [c_void_p, c_char_p, POINTER(c_uint64), c_char_p, c_int32]
    xmem_decompress.restype = c_uint32

    xmem_decompress_stream = _dll.XMemDecompressStream
    xmem_decompress_stream.argtypes = [c_void_p, c_char_p, POINTER(c_int32), c_char_p, POINTER(c_int32)]
    xmem_decompress_stream.restype = c_uint32

    xmem_reset_decompression_context = _dll.XMemResetDecompressionContext
    xmem_reset_decompression_context.argtypes = [c_void_p]
    xmem_reset_decompression_context.restype = c_uint32

    XMCDERR_MOREDATA = 0x81DE2001


class XCompress:
    def __init__(self):
        pass
