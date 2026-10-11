import cv2
import asyncio
import numpy as np
from io import BytesIO
from traceless_watermark import (
    TracelessWatermark,
    WatermarkSuccess,
    WatermarkBlockSize,
    StandardWatermarkErrorCorrectionLevel,
    CustomWatermarkErrorCorrectionLevel
)
from fastapi import APIRouter, UploadFile, Form, File, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse

from ..root_router import root_router

watermark_router = APIRouter(
    prefix="/watermark",
    tags=["watermark"]
)
root_router.include_router(watermark_router)


@watermark_router.post("/encode")
async def encode_watermark(
    text: str = Form(...),
    block_size: WatermarkBlockSize | int = Form(WatermarkBlockSize.FOUR),
    correction_level: StandardWatermarkErrorCorrectionLevel | float = Form(StandardWatermarkErrorCorrectionLevel.MEDIUM),
    file_format: str = Form(".png"),
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    nparr = await asyncio.to_thread(
        np.frombuffer,
        image_bytes,
        np.uint8
    )
    del image_bytes # free memory

    img = await asyncio.to_thread(
        cv2.imdecode,
        nparr,
        cv2.IMREAD_COLOR
    )
    del nparr # free memory

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    watermark = TracelessWatermark(
        block_size = block_size,
        correction_level = correction_level if isinstance(correction_level, StandardWatermarkErrorCorrectionLevel) else CustomWatermarkErrorCorrectionLevel(correction_level)
    )
    watermark_text = text

    encode_result = await watermark.encode_text(img, watermark_text)
    del img # free memory

    if isinstance(encode_result, WatermarkSuccess):
        watermarked_image = encode_result.value
        success, result = await asyncio.to_thread(
            cv2.imencode,
            file_format,
            watermarked_image
        )
        del watermarked_image # free memory

        if success:
            return StreamingResponse(
                content = BytesIO(result.tobytes())
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to encode image")
    else:
        raise HTTPException(status_code=500, detail="Failed to add a watermark.")

@watermark_router.post("/decode")
async def decode_watermark(
    bytes_count: int = Form(...),
    block_size: WatermarkBlockSize | int = Form(WatermarkBlockSize.FOUR),
    correction_level: StandardWatermarkErrorCorrectionLevel | float = Form(StandardWatermarkErrorCorrectionLevel.MEDIUM),
    file: UploadFile = File(...)
):
    image_bytes = await file.read()

    nparr = await asyncio.to_thread(
        np.frombuffer,
        image_bytes,
        np.uint8
    )
    del image_bytes # free memory

    img = await asyncio.to_thread(
        cv2.imdecode,
        nparr,
        cv2.IMREAD_COLOR
    )
    del nparr # free memory

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    watermark = TracelessWatermark(
        block_size = block_size,
        correction_level = correction_level if isinstance(correction_level, StandardWatermarkErrorCorrectionLevel) else CustomWatermarkErrorCorrectionLevel(correction_level)
    )

    decode_result = await watermark.decode_text(img, bytes_count)
    del img # free memory

    if isinstance(decode_result, WatermarkSuccess):
        decoded_payload = decode_result.value

        return PlainTextResponse(
            content = decoded_payload.payload
        )
    else:
        if hasattr(decode_result.error, "cause"):
            raise HTTPException(status_code=500, detail=str(decode_result.error.cause)) # type: ignore
        else:
            raise HTTPException(status_code=500, detail=decode_result.error.__class__.__name__)