"""
Pydantic Data Models for AI Fitness Assistant API
"""

from .auth_models import UserRegister, UserLogin, UserProfile, TokenResponse, UpdateProfile, UserStats
from .chat_models import ChatRequest, ChatResponse, ConversationHistory, ConversationMessage, ConversationsList
from .health_models import HealthResponse, HealthStatus, ModelStatus, ReadinessResponse, LivenessResponse
from .error_models import (
    ErrorResponse, 
    ValidationErrorResponse, 
    AuthenticationErrorResponse,
    AuthorizationErrorResponse,
    RateLimitErrorResponse,
    ServerErrorResponse
)
from .base_models import BaseTimestamp, BaseResponse, PaginationParams, PaginatedResponse

__all__ = [
    # Auth models
    "UserRegister",
    "UserLogin", 
    "UserProfile",
    "TokenResponse",
    "UpdateProfile",
    "UserStats",
    # Chat models
    "ChatRequest",
    "ChatResponse",
    "ConversationHistory",
    "ConversationMessage",
    "ConversationsList",
    # Health models
    "HealthResponse",
    "HealthStatus",
    "ModelStatus",
    "ReadinessResponse", 
    "LivenessResponse",
    # Error models
    "ErrorResponse",
    "ValidationErrorResponse",
    "AuthenticationErrorResponse",
    "AuthorizationErrorResponse", 
    "RateLimitErrorResponse",
    "ServerErrorResponse",
    # Base models
    "BaseTimestamp",
    "BaseResponse",
    "PaginationParams",
    "PaginatedResponse"
]