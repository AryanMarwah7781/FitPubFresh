"""
Chat and Conversation Models
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID to continue existing chat")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the AI")
    
    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "message": "What's a good workout for building chest muscles?",
                "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000",
                "context": {
                    "user_level": "intermediate",
                    "available_equipment": ["dumbbells", "bench"]
                }
            }
        }


class ChatResponse(BaseModel):
    """Chat response from AI"""
    message: str = Field(..., description="Original user message")
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation identifier")
    timestamp: datetime = Field(..., description="Response timestamp")
    tokens_used: int = Field(..., description="Number of tokens used")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What's a good workout for building chest muscles?",
                "response": "For chest development, I recommend focusing on compound movements like bench press, push-ups, and dips...",
                "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2023-09-28T15:30:00Z",
                "tokens_used": 45,
                "response_time_ms": 1200
            }
        }


class ConversationMessage(BaseModel):
    """Individual conversation message"""
    message_id: str = Field(..., description="Unique message identifier")
    user_message: str = Field(..., description="User's message")
    ai_response: str = Field(..., description="AI's response")
    timestamp: datetime = Field(..., description="Message timestamp")
    tokens_used: int = Field(..., description="Tokens used for this exchange")
    context: Optional[Dict[str, Any]] = Field(None, description="Message context")


class ConversationHistory(BaseModel):
    """Conversation history response"""
    user_id: str = Field(..., description="User identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    messages: List[ConversationMessage] = Field(..., description="List of conversation messages")
    total_messages: int = Field(..., description="Total number of messages in conversation")
    created_at: datetime = Field(..., description="Conversation start time")
    last_updated: datetime = Field(..., description="Last message timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "conversation_id": "conv-123e4567-e89b-12d3-a456-426614174000",
                "messages": [
                    {
                        "message_id": "msg-1",
                        "user_message": "Hello",
                        "ai_response": "Hi! How can I help with your fitness journey today?",
                        "timestamp": "2023-09-28T15:30:00Z",
                        "tokens_used": 15,
                        "context": {}
                    }
                ],
                "total_messages": 1,
                "created_at": "2023-09-28T15:30:00Z",
                "last_updated": "2023-09-28T15:30:00Z"
            }
        }


class ConversationsList(BaseModel):
    """List of user conversations"""
    user_id: str = Field(..., description="User identifier")
    conversations: List[Dict[str, Any]] = Field(..., description="List of conversation summaries")
    total_conversations: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Query limit")
    offset: int = Field(..., description="Query offset")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "conversations": [
                    {
                        "conversation_id": "conv-123",
                        "first_message": "What's a good workout routine?",
                        "last_message_time": "2023-09-28T15:30:00Z",
                        "message_count": 5
                    }
                ],
                "total_conversations": 10,
                "limit": 50,
                "offset": 0
            }
        }