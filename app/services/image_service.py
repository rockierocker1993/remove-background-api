import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from app.config.settings import settings
from app.models.schemas import ImageType
import logging

logger = logging.getLogger(__name__)


class ImageService:
    """Service for image processing operations."""
    
    @staticmethod
    def detect_image_type(image_bytes: bytes) -> ImageType:
        """
        Detect image type using advanced heuristics - 4 main categories.
        
        Categories:
        1. ICON: Small, simple graphics (logos, icons, symbols)
        2. STICKER: Flat colored graphics with outlines (stickers, emoji)
        3. CARTOON: Illustrated content (anime, cartoon, characters)
        4. PHOTO: Real photographs (portraits, products, landscapes)
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            ImageType enum (ICON, STICKER, CARTOON, or PHOTO)
        """
        try:
            # Load image
            image = Image.open(BytesIO(image_bytes))
            width, height = image.size
            image_rgb = image.convert("RGB")
            img = np.array(image_rgb)
            
            # Basic metrics
            total_pixels = width * height
            
            # Color analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            saturation = hsv[:, :, 1]
            value = hsv[:, :, 2]
            
            sat_mean = np.mean(saturation)
            sat_std = np.std(saturation)
            value_mean = np.mean(value)
            
            # Edge detection
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.mean(edges > 0)
            
            # Strong edge detection (for outlines)
            edges_strong = cv2.Canny(gray, 200, 300)
            strong_edge_density = np.mean(edges_strong > 0)
            
            # Color histogram analysis
            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hist_peaks = len([i for i in range(1, len(hist_h)-1) 
                            if hist_h[i] > hist_h[i-1] and hist_h[i] > hist_h[i+1] 
                            and hist_h[i] > np.max(hist_h) * 0.1])
            
            # Gradient magnitude for texture
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            texture_complexity = np.std(gradient_magnitude)
            
            logger.info(f"Analysis | Size: {width}x{height} ({total_pixels} px) | Sat: {sat_mean:.1f}±{sat_std:.1f}")
            logger.info(f"Edge: {edge_density:.3f} | Strong: {strong_edge_density:.3f} | Peaks: {hist_peaks} | Texture: {texture_complexity:.1f}")
            
            # === CLASSIFICATION RULES (4 categories) ===
            
            # 1. ICON: Small size, simple graphics, limited colors
            if (total_pixels < 250000 and  # < 250K pixels (~500x500)
                strong_edge_density > 0.015 and  # Has clear edges
                hist_peaks <= 10 and  # Limited color palette
                sat_std < 75):  # Consistent colors
                logger.info("✓ Detected as ICON")
                return ImageType.ICON
            
            # 2. STICKER: Strong outlines, flat colors, medium complexity
            if (strong_edge_density > 0.012 and  # Clear outlines
                sat_mean > 50 and  # Has colors (not grayscale)
                sat_std < 70 and  # Flat, consistent colors
                texture_complexity < 45 and  # Low texture
                hist_peaks <= 15):  # Limited palette
                logger.info("✓ Detected as STICKER")
                return ImageType.STICKER
            
            # 3. CARTOON: Illustrated content (anime, cartoon, characters)
            # Has some outlines OR low texture with good saturation
            if ((strong_edge_density > 0.008 or  # Some outlines
                 (texture_complexity < 50 and sat_mean > 60)) and  # OR low texture + colorful
                sat_std < 80 and  # Relatively consistent
                edge_density < 0.2):  # Not overly complex
                logger.info("✓ Detected as CARTOON")
                return ImageType.CARTOON
            
            # 4. PHOTO: Everything else (realistic, high texture, natural)
            logger.info("✓ Detected as PHOTO")
            return ImageType.PHOTO
            
        except Exception as e:
            logger.error(f"Error in image detection: {e}")
            # Default fallback
            return ImageType.PHOTO
    
    @staticmethod
    def apply_hard_edge_alpha(image: Image.Image, threshold: int = None) -> Image.Image:
        """
        Apply hard edge to alpha channel for crisp icon edges.
        
        Args:
            image: PIL Image in RGBA format
            threshold: Alpha threshold value (default from settings)
            
        Returns:
            PIL Image with hard edge alpha
        """
        if threshold is None:
            threshold = settings.ICON_ALPHA_THRESHOLD
            
        r, g, b, a = image.split()
        # Apply hard threshold: fully transparent or fully opaque
        a = a.point(lambda p: 255 if p > threshold else 0)
        return Image.merge("RGBA", (r, g, b, a))
    
    @staticmethod
    def auto_crop_transparent(image: Image.Image) -> Image.Image:
        """
        Auto crop image to remove transparent borders.
        
        Args:
            image: PIL Image in RGBA format
            
        Returns:
            Cropped PIL Image
        """
        bbox = image.getbbox()
        if bbox:
            return image.crop(bbox)
        return image
    
    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = "PNG", optimize: bool = True) -> bytes:
        """
        Convert PIL Image to bytes.
        
        Args:
            image: PIL Image
            format: Output format (PNG, JPEG, etc.)
            optimize: Whether to optimize the output
            
        Returns:
            Image as bytes
        """
        buf = BytesIO()
        image.save(buf, format, optimize=optimize)
        return buf.getvalue()
