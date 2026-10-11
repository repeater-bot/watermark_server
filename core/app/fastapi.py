from ..api import root_router
from fastapi import FastAPI, Request, Response
from .._info import __version__
from typing import Callable, Awaitable
from loguru import logger

app = FastAPI(
    title = "Watermark Server",
    description = "Generating spectral steganography watermarking.",
    version = __version__,
)

# Add all routers
app.include_router(root_router)

@app.middleware("http")
async def http_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception("Exception in http_middleware")
    return response
