"""
Configuration settings for the application
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_TITLE: str = "Enhanced Solar Rooftop Analysis API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Solar Analysis Settings
    DEFAULT_PANEL_POWER: float = 400  # watts
    DEFAULT_PANEL_EFFICIENCY: float = 0.20
    DEFAULT_PANEL_AREA: float = 2.0  # m²
    DEFAULT_ELECTRICITY_RATE: float = 0.12  # $/kWh

    # File Paths
    OUTPUT_DIR: str = "output"
    MAPS_DIR: str = "output/maps"
    REPORTS_DIR: str = "output/reports"
    OVERLAYS_DIR: str = "output/overlays"

    def __post_init__(self):
        """Ensure output directories exist"""
        dirs = [self.OUTPUT_DIR, self.MAPS_DIR, self.REPORTS_DIR, self.OVERLAYS_DIR]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings instance"""
    return Settings()
