import logging.config
from typing import Callable

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.routers import router
from app.settings import settings
from app.middleware import RequestIdMiddleware
from app.services import process_gif

import uvicorn


logger = logging.getLogger(__name__)

# Dependency Injector
class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    process_gif_service: Callable = providers.Factory(process_gif)

container = Container()
container.config.from_pydantic(settings)

async def lifespan(app: FastAPI):
    """Lifespan to initialize and finalize resources."""
    container.init_resources()
    container.wire(modules=[__name__])
    yield
    container.shutdown_resources()

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust to specific origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
    )
