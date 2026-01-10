from rembg import remove, new_session
from io import BytesIO
from PIL import Image
from app.config.settings import settings
from app.services.image_service import ImageService
from app.models.schemas import ImageType
import logging

logger = logging.getLogger(__name__)


class BackgroundRemovalService:
    """Service for background removal operations."""
    
    # Model mapping for 4 main image categories
    MODEL_MAPPING = {
        ImageType.CARTOON: "isnet-general-use",      # Best for illustrated content
        ImageType.STICKER: "isnet-general-use",      # Best for flat colors with outlines
        ImageType.ICON: "u2net",               # Fast and crisp for simple graphics
        ImageType.PHOTO: "isnet-general-use"   # Best for realistic photos
    }
    
    def __init__(self):
        """Initialize background removal service."""
        self._sessions = {}  # Cache for loaded models
        self.image_service = ImageService()
        logger.info("BackgroundRemovalService initialized with model auto-selection")
    
    def get_session(self, model_name: str):
        """Get or create session for specified model."""
        if model_name not in self._sessions:
            logger.info(f"Loading model: {model_name}...")
            self._sessions[model_name] = new_session(model_name)
            logger.info(f"Model {model_name} loaded successfully")
        return self._sessions[model_name]
    
    def select_model_for_image_type(self, image_type: ImageType) -> str:
        """Select best model based on detected image type."""
        model = self.MODEL_MAPPING.get(image_type, "isnet-general-use")
        logger.info(f"Selected model '{model}' for image type '{image_type.value}'")
        return model
    
    def remove_background_for_icon(self, image_bytes: bytes) -> tuple[bytes, ImageType]:
        """
        Remove background optimized for icon creation with hard edges.
        Auto-selects best model based on image type detection.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (processed image bytes, detected image type)
        """
        # Detect image type
        image_type = self.image_service.detect_image_type(image_bytes)
        
        # Select best model for this image type
        model_name = self.select_model_for_image_type(image_type)
        session = self.get_session(model_name)
        
        # Remove background
        output_bytes = remove(image_bytes, session=session)
        
        # Load as RGBA
        img = Image.open(BytesIO(output_bytes)).convert("RGBA")
        
        # Apply hard edge for crisp icons
        img = self.image_service.apply_hard_edge_alpha(img)
        
        # Auto crop to remove transparent borders
        img = self.image_service.auto_crop_transparent(img)
        
        # Convert to bytes
        final_bytes = self.image_service.image_to_bytes(img, format="PNG", optimize=True)
        
        return final_bytes, image_type
    
    def remove_background_standard(self, image_bytes: bytes) -> tuple[bytes, ImageType]:
        """
        Remove background with standard settings (soft edges).
        Auto-selects best model based on image type detection.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (processed image bytes, detected image type)
        """
        # Detect image type
        image_type = self.image_service.detect_image_type(image_bytes)
        
        # Select best model for this image type
        model_name = self.select_model_for_image_type(image_type)
        session = self.get_session(model_name)
        
        # Remove background
        output_bytes = remove(image_bytes, session=session)
        
        # Load as RGBA
        img = Image.open(BytesIO(output_bytes)).convert("RGBA")
        
        # Auto crop
        img = self.image_service.auto_crop_transparent(img)
        
        # Convert to bytes
        final_bytes = self.image_service.image_to_bytes(img, format="PNG", optimize=True)
        
        return final_bytes, image_type

    def remove_background(self, image_bytes: bytes, model_name: str) -> bytes:
        logger.info(f"Removing background using model: {model_name}")
        session = self.get_session(model_name)
        # Remove background
        output_bytes = remove(image_bytes, session=session)
        logger.info(f"Background removed using model: {model_name}")
        return output_bytes
