"""
Health Check and System Status Models
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ModelStatus(BaseModel):
    """AI Model status information"""
    loaded: bool = Field(..., description="Whether the model is loaded")
    model_name: Optional[str] = Field(None, description="Name of the loaded model")
    model_path: Optional[str] = Field(None, description="Path to the model")
    memory_usage_mb: Optional[float] = Field(None, description="Model memory usage in MB")
    last_inference_time: Optional[datetime] = Field(None, description="Last successful inference")
    
    class Config:
        json_schema_extra = {
            "example": {
                "loaded": True,
                "model_name": "mistral-7b-instruct",
                "model_path": "/app/models/mistral-7b-instruct",
                "memory_usage_mb": 13500.5,
                "last_inference_time": "2023-09-28T15:29:45Z"
            }
        }


class DatabaseStatus(BaseModel):
    """Database connection status"""
    connected: bool = Field(..., description="Database connection status")
    connection_pool_size: Optional[int] = Field(None, description="Active connections")
    last_query_time: Optional[datetime] = Field(None, description="Last successful query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "connected": True,
                "connection_pool_size": 5,
                "last_query_time": "2023-09-28T15:30:00Z"
            }
        }


class SystemMetrics(BaseModel):
    """System performance metrics"""
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")
    memory_usage_percent: Optional[float] = Field(None, description="Memory usage percentage")
    disk_usage_percent: Optional[float] = Field(None, description="Disk usage percentage")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cpu_usage_percent": 25.5,
                "memory_usage_percent": 68.2,
                "disk_usage_percent": 45.0,
                "uptime_seconds": 86400.5
            }
        }


class HealthResponse(BaseModel):
    """Comprehensive health check response"""
    status: HealthStatus = Field(..., description="Overall system health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(..., description="API version")
    environment: str = Field(default="production", description="Deployment environment")
    
    # Component status
    model_status: ModelStatus = Field(..., description="AI model status")
    database_status: Optional[DatabaseStatus] = Field(None, description="Database status")
    
    # System metrics
    system_metrics: SystemMetrics = Field(..., description="System performance metrics")
    
    # Additional details
    checks_passed: int = Field(..., description="Number of successful health checks")
    checks_total: int = Field(..., description="Total number of health checks")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2023-09-28T15:30:00Z",
                "version": "1.0.0",
                "environment": "production",
                "model_status": {
                    "loaded": True,
                    "model_name": "mistral-7b-instruct",
                    "model_path": "/app/models/mistral-7b-instruct",
                    "memory_usage_mb": 13500.5,
                    "last_inference_time": "2023-09-28T15:29:45Z"
                },
                "database_status": {
                    "connected": True,
                    "connection_pool_size": 5,
                    "last_query_time": "2023-09-28T15:30:00Z"
                },
                "system_metrics": {
                    "cpu_usage_percent": 25.5,
                    "memory_usage_percent": 68.2,
                    "disk_usage_percent": 45.0,
                    "uptime_seconds": 86400.5
                },
                "checks_passed": 4,
                "checks_total": 4,
                "details": {
                    "kubernetes_ready": True,
                    "load_balancer_healthy": True
                }
            }
        }


class ReadinessResponse(BaseModel):
    """Kubernetes readiness probe response"""
    ready: bool = Field(..., description="Service readiness status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, bool] = Field(..., description="Individual readiness checks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ready": True,
                "timestamp": "2023-09-28T15:30:00Z",
                "checks": {
                    "model_loaded": True,
                    "database_connected": True,
                    "cache_available": True
                }
            }
        }


class LivenessResponse(BaseModel):
    """Kubernetes liveness probe response"""
    alive: bool = Field(..., description="Service liveness status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float = Field(..., description="Service uptime")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alive": True,
                "timestamp": "2023-09-28T15:30:00Z",
                "uptime_seconds": 3600.5
            }
        }