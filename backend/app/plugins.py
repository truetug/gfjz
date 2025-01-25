from typing import Any, Tuple, Dict, List, Union
from io import BytesIO
import zipfile
from PIL import Image, ImageOps
from app.schemas import ResizeParams, FlipParams, PadParams, CropParams, RotateParams, PipelineStep

# Plugin implementations
def plugin_resize(img: Image.Image, params: ResizeParams) -> Image.Image:
    """Resize the image to the specified size while maintaining aspect ratio."""
    return img.resize(params.size, resample=Image.Resampling.LANCZOS)

def plugin_flip(img: Image.Image, params: FlipParams) -> Image.Image:
    """Flip the image based on mode: vertical, horizontal, or both."""
    if params.mode == "vertical":
        img = ImageOps.flip(img)
    elif params.mode == "horizontal":
        img = ImageOps.mirror(img)
    elif params.mode == "both":
        img = ImageOps.mirror(ImageOps.flip(img))
    return img

def plugin_pad(img: Image.Image, params: PadParams) -> Image.Image:
    """Add padding to the image to make it match the target size."""
    color_hex = params.color.as_hex() if hasattr(params.color, "as_hex") else params.color
    return ImageOps.pad(img, params.target_size, color=color_hex, centering=params.centering)

def plugin_crop(img: Image.Image, params: CropParams) -> Image.Image:
    """Crop the image to the specified coordinates."""
    return img.crop(params.coordinates)

def plugin_rotate(img: Image.Image, params: RotateParams) -> Image.Image:
    """Rotate the image by a specified angle."""
    return img.rotate(params.angle, expand=True)

# Plugin mapping
plugin_mapping: Dict[str, Any] = {
    "resize": plugin_resize,
    "flip": plugin_flip,
    "pad": plugin_pad,
    "crop": plugin_crop,
    "rotate": plugin_rotate,
}

def process_frame(img: Image.Image, pipeline: List[PipelineStep]) -> Image.Image:
    """Process an individual frame using a sequence of pipeline steps."""
    for step in pipeline:
        plugin = plugin_mapping.get(step.plugin)
        if plugin:
            img = plugin(img, step.params)
        else:
            raise ValueError(f"Plugin {step.plugin} not found.")
    return img

def archive_frames(frames: List[Image.Image], output_format: str) -> BytesIO:
    """Archive frames in a specified format into a ZIP file in memory."""
    output_zip = BytesIO()
    with zipfile.ZipFile(output_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for i, frame in enumerate(frames):
            frame_bytes = BytesIO()
            frame.save(frame_bytes, format=output_format)
            frame_bytes.seek(0)
            zf.writestr(f"frame_{i}.{output_format.lower()}", frame_bytes.read())
    output_zip.seek(0)
    return output_zip
