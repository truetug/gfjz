from typing import Tuple, List, Union
from pydantic import BaseModel, Field
from pydantic.color import Color

class ResizeParams(BaseModel):
    size: Tuple[int, int] = Field(..., description="Target size for resizing")

class FlipParams(BaseModel):
    mode: str = Field(..., description="Flip mode: vertical, horizontal, or both")

class PadParams(BaseModel):
    target_size: Tuple[int, int] = Field(..., description="Target size for padding")
    color: Union[Color, Tuple[int, int, int]] = Field((0, 0, 0), description="Padding color")
    centering: Tuple[float, float] = Field((0.5, 0.5), description="Centering of the image during padding")

class CropParams(BaseModel):
    coordinates: Tuple[int, int, int, int] = Field(..., description="Coordinates for cropping")

class RotateParams(BaseModel):
    angle: int = Field(..., description="Angle to rotate the image, in degrees")

class PipelineStep(BaseModel):
    plugin: str
    params: Union[ResizeParams, FlipParams, PadParams, CropParams, RotateParams]

class PluginConfig(BaseModel):
    pipeline: List[PipelineStep]
    create_preview: bool = Field(True, description="Whether to create a GIF preview")
    output_format: str = Field("GIF", description="Output format: GIF, PNG, or JPEG")
    output_filename: str = Field("output", description="Name of the output file")
