from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    pass


class InvalidImageError(Exception):
    """Custom exception for invalid image inputs."""
    pass


async def image_processing_exception_handler(request: Request, exc: ImageProcessingError):
    """Handler for image processing errors."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Image processing failed: {str(exc)}",
            "type": "image_processing_error"
        }
    )


async def invalid_image_exception_handler(request: Request, exc: InvalidImageError):
    """Handler for invalid image errors."""
    return JSONResponse(
        status_code=400,
        content={
            "detail": f"Invalid image: {str(exc)}",
            "type": "invalid_image_error"
        }
    )
