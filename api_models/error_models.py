"""
Error Response Models
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "error_code": "VALIDATION_ERROR"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(default=False, description="Request success status")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "timestamp": "2023-09-28T15:30:00Z",
                "request_id": "req-123e4567-e89b-12d3-a456-426614174000",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "error_code": "INVALID_FORMAT"
                    }
                ]
            }
        }


class ValidationErrorResponse(BaseModel):
    """Pydantic validation error response"""
    success: bool = Field(default=False)
    error: str = Field(default="VALIDATION_ERROR")
    message: str = Field(default="Request validation failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    validation_errors: List[Dict[str, Any]] = Field(..., description="Pydantic validation errors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "timestamp": "2023-09-28T15:30:00Z",
                "validation_errors": [
                    {
                        "loc": ["password"],
                        "msg": "ensure this value has at least 8 characters",
                        "type": "value_error.any_str.min_length"
                    }
                ]
            }
        }


class AuthenticationErrorResponse(BaseModel):
    """Authentication error response"""
    success: bool = Field(default=False)
    error: str = Field(default="AUTHENTICATION_ERROR")
    message: str = Field(..., description="Authentication error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "AUTHENTICATION_ERROR",
                "message": "Invalid credentials provided",
                "timestamp": "2023-09-28T15:30:00Z"
            }
        }


class AuthorizationErrorResponse(BaseModel):
    """Authorization error response"""
    success: bool = Field(default=False)
    error: str = Field(default="AUTHORIZATION_ERROR")
    message: str = Field(..., description="Authorization error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    required_permission: Optional[str] = Field(None, description="Required permission")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "AUTHORIZATION_ERROR",
                "message": "Insufficient permissions to access this resource",
                "timestamp": "2023-09-28T15:30:00Z",
                "required_permission": "admin"
            }
        }


class RateLimitErrorResponse(BaseModel):
    """Rate limit error response"""
    success: bool = Field(default=False)
    error: str = Field(default="RATE_LIMIT_EXCEEDED")
    message: str = Field(..., description="Rate limit error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retry_after_seconds: int = Field(..., description="Seconds to wait before retry")
    limit: int = Field(..., description="Rate limit threshold")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
                "timestamp": "2023-09-28T15:30:00Z",
                "retry_after_seconds": 60,
                "limit": 100
            }
        }


class ServerErrorResponse(BaseModel):
    """Internal server error response"""
    success: bool = Field(default=False)
    error: str = Field(default="INTERNAL_SERVER_ERROR")
    message: str = Field(default="An internal server error occurred")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_id: Optional[str] = Field(None, description="Internal error tracking ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "timestamp": "2023-09-28T15:30:00Z",
                "error_id": "err-123e4567-e89b-12d3-a456-426614174000"
            }
        }