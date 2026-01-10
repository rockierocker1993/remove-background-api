from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    APP_NAME: str = "Background Removal Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    # Model Settings
    DEFAULT_MODEL: str = "isnet-general-use"
    ANIME_MODEL: str = "isnet-anime"
    
    # Image Processing Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["jpg", "jpeg", "png", "webp"]
    
    # Edge Detection Thresholds
    ICON_ALPHA_THRESHOLD: int = 200
    SATURATION_MEAN_THRESHOLD: int = 80
    SATURATION_STD_THRESHOLD: int = 60
    EDGE_DENSITY_THRESHOLD: float = 0.15
    
    # Storage Settings
    STORAGE_PATH: str = "./storage"
    ENABLE_STORAGE: bool = True  # Toggle to enable/disable file storage
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields


settings = Settings(_env_file=None)  # Don't load .env file by default
