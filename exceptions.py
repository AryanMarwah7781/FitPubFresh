"""
Exception Handlers for AI Fitness Assistant API
"""

import logging
import traceback
import uuid
from datetime import datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Union

from models.error_models import (
    ErrorResponse,
    ValidationErrorResponse,
    AuthenticationErrorResponse,
    AuthorizationErrorResponse,
    ServerErrorResponse
)

# Configure logger
logger = logging.getLogger(__name__)


class APIException(HTTPException):
    """Custom API Exception with enhanced error handling"""
    
    def __init__(
        self,
        status_code: int,
        error_type: str,
        message: str,
        details: list = None,
        request_id: str = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.error_type = error_type
        self.message = message
        self.details = details or []
        self.request_id = request_id or str(uuid.uuid4())


class AuthenticationException(APIException):
    """Authentication related exceptions"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="AUTHENTICATION_ERROR",
            message=message
        )


class AuthorizationException(APIException):
    """Authorization related exceptions"""
    
    def __init__(self, message: str = "Insufficient permissions", required_permission: str = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_type="AUTHORIZATION_ERROR", 
            message=message
        )
        self.required_permission = required_permission


class RateLimitException(APIException):
    """Rate limiting exceptions"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60, limit: int = 100):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_type="RATE_LIMIT_EXCEEDED",
            message=message
        )
        self.retry_after = retry_after
        self.limit = limit


class ModelException(APIException):
    """AI Model related exceptions"""
    
    def __init__(self, message: str = "AI model error"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_type="MODEL_ERROR",
            message=message
        )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions"""
    logger.error(f"API Exception: {exc.error_type} - {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error_type,
            message=exc.message,
            request_id=exc.request_id,
            details=exc.details
        ).dict()
    )


async def validation_exception_handler(request: Request, exc: Union[RequestValidationError, ValidationError]) -> JSONResponse:
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc}")
    
    # Extract validation errors
    validation_errors = []
    if hasattr(exc, 'errors'):
        validation_errors = exc.errors()
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse(
            validation_errors=validation_errors
        ).dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    # Map common HTTP exceptions to our error format
    error_type_map = {
        401: "AUTHENTICATION_ERROR",
        403: "AUTHORIZATION_ERROR", 
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_type = error_type_map.get(exc.status_code, "HTTP_ERROR")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=error_type,
            message=str(exc.detail)
        ).dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    error_id = str(uuid.uuid4())
    logger.error(f"Unhandled exception [{error_id}]: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ServerErrorResponse(
            message="An internal server error occurred",
            error_id=error_id
        ).dict()
    )


def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI app"""
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)