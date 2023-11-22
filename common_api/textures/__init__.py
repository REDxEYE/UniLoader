import bpy
import numpy as np

from .texture_decoder import Texture, PixelFormat, get_buffer_size_from_texture_format, \
    get_uncompressed_pixel_format_variant, is_compressed_pixel_format, lz4_decompress, zstd_decompress

to_4c_remap = {
    PixelFormat.RGBA32: PixelFormat.RGBA32,
    PixelFormat.RGB32: PixelFormat.RGBA32,
    PixelFormat.RG32: PixelFormat.RGBA32,
    PixelFormat.R32: PixelFormat.RGBA32,
    PixelFormat.RGBA16: PixelFormat.RGBA16,
    PixelFormat.RGB16: PixelFormat.RGBA16,
    PixelFormat.RG16: PixelFormat.RGBA16,
    PixelFormat.RG16_SIGNED: PixelFormat.RGBA16,
    PixelFormat.R16: PixelFormat.RGBA16,
    PixelFormat.RGBA32F: PixelFormat.RGBA32F,
    PixelFormat.RGB32F: PixelFormat.RGBA32F,
    PixelFormat.RG32F: PixelFormat.RGBA32F,
    PixelFormat.R32F: PixelFormat.RGBA32F,
    PixelFormat.RGBA16F: PixelFormat.RGBA16F,
    PixelFormat.RGB16F: PixelFormat.RGBA16F,
    PixelFormat.RG16F: PixelFormat.RGBA16F,
    PixelFormat.R16F: PixelFormat.RGBA16F,
    PixelFormat.RGBA8888: PixelFormat.RGBA8888,
    PixelFormat.BGRA8888: PixelFormat.BGRA8888,
    PixelFormat.RGB888: PixelFormat.RGBA8888,
    PixelFormat.RG88: PixelFormat.RGBA8888,
    PixelFormat.RA88: PixelFormat.RGBA8888,
    PixelFormat.R8: PixelFormat.RGBA8888,
    PixelFormat.RGB565: PixelFormat.RGBA8888,
    PixelFormat.RGBA5551: PixelFormat.RGBA8888,
    PixelFormat.RGBA1010102: PixelFormat.RGBA16,
    PixelFormat.BC1: PixelFormat.RGBA8888,
    PixelFormat.BC1a: PixelFormat.RGBA8888,
    PixelFormat.BC2: PixelFormat.RGBA8888,
    PixelFormat.BC3: PixelFormat.RGBA8888,
    PixelFormat.BC4: PixelFormat.RGBA8888,
    PixelFormat.BC5: PixelFormat.RGBA8888,
    PixelFormat.BC6: PixelFormat.RGBA8888,
    PixelFormat.BC7: PixelFormat.RGBA8888,
}


def create_image_from_data(name, data: bytes, width: int, height: int, pixel_format: PixelFormat,
                           flip_ud: bool = False, flip_lr: bool = False):
    pixels: np.ndarray
    if pixel_format == PixelFormat.RGBA8888:
        pixels = np.frombuffer(data, np.uint8).astype(np.float32) / 0xFF
    elif pixel_format == PixelFormat.RGBA16:
        pixels = np.frombuffer(data, np.uint16).astype(np.float32) / 0xFFFF
    elif pixel_format == PixelFormat.RGBA32:
        pixels = np.frombuffer(data, np.uint32).astype(np.float32) / 0xFFFFFFFF
    elif pixel_format == PixelFormat.RGBA16F:
        pixels = np.frombuffer(data, np.float16).astype(np.float32)
    elif pixel_format == PixelFormat.RGBA32F:
        pixels = np.frombuffer(data, np.float32)
    else:
        texture = Texture.from_data(data, width, height, pixel_format)
        texture = texture.convert_to(to_4c_remap[pixel_format])
        if texture is None:
            return None
        return create_image_from_data(name, texture.data, width, height, to_4c_remap[pixel_format])
    pixels = pixels.reshape((width, height, -1))
    if flip_ud:
        pixels = np.flipud(pixels)
    if flip_lr:
        pixels = np.fliplr(pixels)

    image = bpy.data.images.new(name, width=width, height=height, alpha=True)
    image.name = name
    image.alpha_mode = "CHANNEL_PACKED"
    # image.file_format = "HDR" if is_hdr else "PNG"
    image.pixels.foreach_set(pixels.ravel())
    image.pack()
    return image


def create_image_from_texture(name, texture: Texture, flip_ud: bool = False, flip_lr: bool = False):
    pixels: np.ndarray
    return create_image_from_data(name, texture.data, texture.width, texture.height, texture.pixel_format, flip_ud,
                                  flip_lr)
