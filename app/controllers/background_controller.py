from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.models.schemas import HealthResponse
from app.config.settings import settings
from app.services import FileStorageService

router = APIRouter()

# Lazy service initialization
_bg_service = None
_storage_service = None

def get_bg_service():
    """Get or create background removal service instance."""
    global _bg_service
    if _bg_service is None:
        from app.services import BackgroundRemovalService
        _bg_service = BackgroundRemovalService()
    return _bg_service

def get_storage_service():
    """Get or create file storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = FileStorageService()
    return _storage_service


@router.post(
    "/remove-bg-icon",
    summary="Remove background for icon creation",
    description="Remove background with hard edges optimized for icon creation",
    response_class=Response,
    tags=["Background Removal"]
)
async def remove_background_icon(file: UploadFile = File(...)):
    """
    Remove background from an image with hard edge alpha for crisp icons.
    
    - **file**: Image file to process (JPG, PNG, WEBP)
    
    Returns PNG image with transparent background.
    """
    try:
        # Read file
        input_bytes = await file.read()
        
        # Validate file
        if not input_bytes:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if len(input_bytes) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Process image
        bg_service = get_bg_service()
        result_bytes, image_type = bg_service.remove_background_standard(input_bytes)
        
        # Save files if storage is enabled
        if settings.ENABLE_STORAGE:
            storage_service = get_storage_service()
            input_path, output_path = storage_service.save_pair(
                input_bytes, 
                result_bytes, 
                image_type,
                file.filename
            )
        
        # Return responsetorage is enabled
        if settings.ENABLE_STORAGE:
            storage_service = get_storage_service()
            input_path, output_path = storage_service.save_pair(
                input_bytes, 
                result_bytes, 
                image_type,
                file.filename
            )
        
        # Return response
        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": 'attachment; filename="result.png"',
                "Content-Length": str(len(result_bytes)),
                "X-Image-Type": image_type.value
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.post(
    "/remove-bg-auto-detect",
    summary="Remove background (standard)",
    description="Remove background with soft edges for general use",
    response_class=Response,
    tags=["Background Removal"]
)
async def remove_background_standard(file: UploadFile = File(...)):
    """
    Remove background from an image with soft edges.
    
    - **file**: Image file to process (JPG, PNG, WEBP)
    
    Returns PNG image with transparent background.
    """
    try:
        # Read file
        input_bytes = await file.read()
        
        # Validate file
        if not input_bytes:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if len(input_bytes) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
            )
        
        # Process image
        bg_service = get_bg_service()
        result_bytes, image_type = bg_service.remove_background_standard(input_bytes)
        
        # Return response
        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": 'attachment; filename="result.png"',
                "Content-Length": str(len(result_bytes)),
                "X-Image-Type": image_type.value
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.post(
    "/remove-bg/{model_name}",
    summary="Remove background (standard)",
    description="Remove background with soft edges for general use",
    response_class=Response,
    tags=["Background Removal"]
)
async def remove_background_standard(model_name: str, file: UploadFile = File(...)):
    """
    Remove background from an image based on specified model.
    """
    try:
        # Read file
        input_bytes = await file.read()
        
        # Validate file
        if not input_bytes:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if len(input_bytes) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
            )
        
        # Process image
        bg_service = get_bg_service()
        result_bytes = bg_service.remove_background(input_bytes, model_name)
        
        # Return response
        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": 'attachment; filename="result.png"',
                "Content-Length": str(len(result_bytes))
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the service is running",
    tags=["Health"]
)
def health_check():
    """
    Health check endpoint to verify service is running.
    """
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION
    )


@router.get(
    "/storage/stats",
    summary="Get storage statistics",
    description="Get file counts for each category",
    tags=["Storage"]
)
def get_storage_stats():
    """
    Get statistics about stored files by category.
    """
    if not settings.ENABLE_STORAGE:
        raise HTTPException(status_code=404, detail="Storage is disabled")
    
    storage_service = get_storage_service()
    stats = storage_service.get_category_stats()
    
    return {
        "storage_path": settings.STORAGE_PATH,
        "categories": stats,
        "total_input": sum(s["input"] for s in stats.values()),
        "total_output": sum(s["output"] for s in stats.values())
    }
