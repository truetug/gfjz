import json
import zipfile
from io import BytesIO
from typing import Any, Dict, List, Tuple, Union
from PIL import Image
from app.plugins import plugin_mapping, process_frame, archive_frames
from app.schemas import PluginConfig
import logging
import argparse

logger = logging.getLogger(__name__)

def process_gif(
    input_gif: Any,
    config: PluginConfig,
) -> Tuple[Union[BytesIO, None], Union[BytesIO, None]]:
    """Process a GIF entirely in memory and optionally create a preview or ZIP archive."""
    logger.info("Starting GIF processing")

    # Ensure input_gif is a readable file-like object
    fp = BytesIO(input_gif.read())
    fp.seek(0)
    gif = Image.open(fp)
    frames = []

    for frame in range(gif.n_frames):
        gif.seek(frame)
        img = gif.convert("RGBA")
        logger.info(f"Processing frame {frame}")
        processed_frame = process_frame(
            img,
            config.pipeline,
        )
        frames.append(processed_frame)

    output_gif = None
    if config.create_preview:
        logger.info("Creating GIF preview")
        output_gif = BytesIO()
        frames[0].save(
            output_gif,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=gif.info.get("duration", 100),
        )
        output_gif.seek(0)

    output_zip = None
    if not config.create_preview:
        logger.info("Creating ZIP archive of frames")
        output_zip = archive_frames(
            frames,
            config.output_format,
        )

    return output_gif, output_zip

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a GIF with plugins.")
    parser.add_argument("--input", required=True, help="Path to the input GIF file")
    parser.add_argument("--config", required=True, help="Path to the JSON configuration file")
    parser.add_argument("--output", required=True, help="Path to save the output file")

    args = parser.parse_args()

    with open(args.config, "r") as config_file:
        config_data = json.load(config_file)

    config = PluginConfig(**config_data)

    with open(args.input, "rb") as input_file:
        input_gif = BytesIO(input_file.read())

    preview_gif, result_zip = process_gif(
        input_gif,
        config,
    )

    if config.create_preview and preview_gif:
        with open(args.output, "wb") as output_file:
            output_file.write(preview_gif.getvalue())
        logger.info(f"Preview saved to {args.output}")

    elif result_zip:
        with open(args.output, "wb") as output_file:
            output_file.write(result_zip.getvalue())
        logger.info(f"ZIP archive saved to {args.output}")
