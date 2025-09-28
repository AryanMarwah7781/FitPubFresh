"""
Base Pydantic Models for Common Patterns
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BaseTimestamp(BaseModel):
    """Base model with timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""
    limit: int = 50
    offset: int = 0
    
    class Config:
        extra = "forbid"


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    total: int
    limit: int
    offset: int
    has_more: bool