"""Application settings and configuration."""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    DEBUG: bool = False
    
    # Data Update Frequencies (in minutes)
    MACRO_UPDATE_FREQ: int = 360  # 6 hours for macro data (daily is too long for real-time)
    CRYPTO_UPDATE_FREQ: int = 60  # 1 hour for crypto data
    SECTOR_UPDATE_FREQ: int = 60  # 1 hour for sector data
    FUNDING_UPDATE_FREQ: int = 480  # 8 hours for funding rates
    FRAGILITY_UPDATE_FREQ: int = 15  # 15 min for fragility
    
    # FRED API Key (optional - some data available without key)
    FRED_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./crypto_dashboard.db"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
