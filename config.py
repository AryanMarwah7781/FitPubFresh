"""
Configuration Settings for AI Fitness Assistant API
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "AI Fitness Assistant API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Security
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    password_salt: str = "fitness-app-salt"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database
    database_url: Optional[str] = None
    async_database_url: Optional[str] = None
    
    # Redis (for caching/sessions)
    redis_url: Optional[str] = None
    
    # AI Model
    model_path: str = "./models/mistral-7b-instruct"
    model_name: str = "mistral-7b-instruct"
    vllm_engine_args: str = "--max-model-len=4096 --dtype=half"
    enable_cuda: bool = True
    mock_ai_responses: bool = True  # Use mock responses by default
    
    # CORS
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # File Upload
    max_file_size_mb: int = 10
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    prometheus_port: int = 9090
    
    # AWS/Kubernetes
    #wrong region configured 
    aws_region: str = "us-east-1"
    eks_cluster_name: str = "ai-fitness-dev"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment variable mapping
        fields = {
            "secret_key": {"env": "SECRET_KEY"},
            "database_url": {"env": "DATABASE_URL"},
            "redis_url": {"env": "REDIS_URL"},
            "model_path": {"env": "MODEL_PATH"},
            "cors_origins": {"env": "CORS_ORIGINS"},
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings