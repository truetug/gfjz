from fastapi import APIRouter, UploadFile, Depends, HTTPException, status, Form
from fastapi.responses import FileResponse
from dependency_injector.wiring import inject, Provide
from app.services import process_gif, PluginConfig
from pydantic import BaseModel
import json
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

router = APIRouter()

class ConfigInput(BaseModel):
    file: UploadFile
    config: PluginConfig

async def parse_config(
    file: UploadFile,
    config: str = Form(...)
) -> ConfigInput:
    config_dict = json.loads(config)
    config_obj = PluginConfig(**config_dict)
    return ConfigInput(file=file, config=config_obj)

@router.post("/process", response_model=None, status_code=status.HTTP_200_OK)
@inject
async def process_gif_endpoint(
    config_input: ConfigInput = Depends(parse_config),
    #process_service: callable = Depends(Provide["process_gif_service"]),
) -> FileResponse:
    logger.info("Received request for GIF processing.")

    # Pass file-like object directly to the service
    preview_gif, result_zip = process_gif(
        BytesIO(await config_input.file.read()),
        config_input.config,
    )

    if config_input.config.create_preview:
        filename = f"{config_input.config.output_filename}.gif"
        with open(filename, "wb") as fp:
            fp.write(preview_gif.getvalue())
        logger.info(f"GIF preview saved to {filename}")
        return FileResponse(
            filename,
            media_type="image/gif",
            filename=filename,
        )

    if result_zip:
        filename = f"{config_input.config.output_filename}.zip"
        with open(filename, "wb") as fp:
            fp.write(result_zip.getvalue())
        logger.info(f"ZIP file saved to {filename}")
        return FileResponse(
            filename,
            media_type="application/zip",
            filename=filename,
        )

    logger.error("No output generated.")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No output generated.",
    )
