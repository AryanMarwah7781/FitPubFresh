"""
Authentication and User Models
"""

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from .base_models import BaseTimestamp


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 chars)")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    fitness_goals: Optional[str] = Field(None, max_length=500, description="User's fitness goals")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        return v
    
    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secure123",
                "first_name": "John",
                "last_name": "Doe",
                "fitness_goals": "Build muscle and improve cardio"
            }
        }


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secure123"
            }
        }


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user_id: str = Field(..., description="User ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class UserProfile(BaseModel):
    """User profile information"""
    user_id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    fitness_goals: Optional[str] = Field(None, description="User's fitness goals")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_active: datetime = Field(..., description="Last activity timestamp")
    is_active: bool = Field(default=True, description="Account status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "fitness_goals": "Build muscle and improve cardio",
                "created_at": "2023-09-27T10:00:00Z",
                "last_active": "2023-09-28T15:30:00Z",
                "is_active": True
            }
        }


class UpdateProfile(BaseModel):
    """Profile update request"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    fitness_goals: Optional[str] = Field(None, max_length=500)
    
    class Config:
        extra = "forbid"


class UserStats(BaseModel):
    """User activity statistics"""
    user_id: str = Field(..., description="User identifier")
    total_conversations: int = Field(..., description="Total number of conversations")
    total_messages: int = Field(..., description="Total messages sent")
    days_active: int = Field(..., description="Days since first activity")
    member_since: datetime = Field(..., description="Account creation date")
    last_active: datetime = Field(..., description="Last activity timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "total_conversations": 25,
                "total_messages": 150,
                "days_active": 15,
                "member_since": "2023-09-01T10:00:00Z",
                "last_active": "2023-09-28T15:30:00Z"
            }
        }