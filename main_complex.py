"""
Production FastAPI Application for AI Fitness Assistant
Enhanced with proper error handling, logging, and production patterns
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import hashlib
import jwt
import os
import uuid
import time
import psutil
from typing import Optional, List, Dict, Any

# Local imports
from config import get_settings
from logging_config import setup_logging, get_logger
from exceptions import setup_exception_handlers, AuthenticationException, ModelException
from models import (
    # Auth models
    UserRegister, UserLogin, UserProfile, TokenResponse, UpdateProfile, UserStats,
    # Chat models  
    ChatRequest, ChatResponse, ConversationHistory,
    # Health models
    HealthResponse, HealthStatus, ModelStatus, SystemMetrics, ReadinessResponse, LivenessResponse,
    # Error models
    ErrorResponse
)

# Configuration and logging
settings = get_settings()
setup_logging(settings.log_level, json_logs=(settings.environment == "production"))
logger = get_logger(__name__)

# Database simulation (in production, use PostgreSQL/MongoDB)
users_db: Dict[str, Dict[str, Any]] = {}
conversations_db: Dict[str, List[Dict[str, Any]]] = {}

# Security
security = HTTPBearer()

# Global state
app_start_time = time.time()
ai_model_loaded = False

# App lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global ai_model_loaded
    
    # Startup
    logger.info("🚀 Starting AI Fitness API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    try:
        if not settings.mock_ai_responses:
            # In production, load the actual AI model here
            # from vllm import LLM
            # global ai_model
            # ai_model = LLM(model=settings.model_path)
            pass
        
        ai_model_loaded = True
        logger.info("✅ AI Model loaded successfully (mock mode)")
    except Exception as e:
        logger.error(f"⚠️  AI Model loading failed: {e}")
        ai_model_loaded = False
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down AI Fitness API...")


# FastAPI App
app = FastAPI(
    title=settings.app_name,
    description="Production-ready API for AI-powered fitness coaching with comprehensive error handling",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Setup exception handlers
# setup_exception_handlers(app)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

if settings.environment == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": f"{process_time:.3f}s"
        }
    )
    
    response.headers["X-Request-ID"] = request_id
    return response

# Utility Functions
def hash_password(password: str) -> str:
    """Hash password with salt"""
    return hashlib.sha256((password + settings.password_salt).encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise AuthenticationException("Invalid authentication credentials")
        return user_id
    except jwt.PyJWTError:
        raise AuthenticationException("Invalid authentication credentials")

def get_current_user(user_id: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get current user from database"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def generate_ai_response(message: str, context: Optional[Dict[str, Any]] = None) -> tuple[str, int]:
    """Generate AI response (mock implementation)"""
    if not ai_model_loaded:
        return "AI model is currently unavailable. Please try again later.", 10
    
    # Mock AI response - in production, use actual model
    fitness_responses = {
        "workout": "Here's a personalized workout plan: Start with 10 minutes of dynamic warm-up, then perform 3 sets of: squats (12 reps), push-ups (10 reps), lunges (10 per leg), and plank (30 seconds). Cool down with 5 minutes of stretching.",
        "nutrition": "For optimal nutrition, aim for: 1.6-2.2g protein per kg body weight, complex carbohydrates from whole grains, healthy fats from nuts/avocado, and 5-9 servings of fruits/vegetables daily. Stay hydrated with 2-3L water.",
        "motivation": "Remember, progress isn't always linear! Every workout, healthy meal, and positive choice builds momentum. Consistency beats perfection - you're building stronger habits with each session. Celebrate small wins!",
        "recovery": "Recovery is crucial for progress! Aim for 7-9 hours of quality sleep, include rest days, try active recovery like walking or gentle yoga, and listen to your body's signals.",
        "cardio": "For effective cardio: Mix steady-state (20-30 min moderate intensity) with HIIT (15-20 min with intervals). Start with 3x/week and gradually increase. Find activities you enjoy - dancing, swimming, hiking!",
    }
    
    message_lower = message.lower()
    for key, response in fitness_responses.items():
        if key in message_lower:
            return response, len(response.split())
    
    # Default personalized response
    response = f"As your AI fitness coach, I understand you're asking about: {message}. Let me help you achieve your fitness goals with personalized advice! What specific aspect would you like me to focus on - workout routines, nutrition, motivation, or recovery strategies?"
    return response, len(response.split())

# System metrics helper
def get_system_metrics() -> SystemMetrics:
    """Get current system performance metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return SystemMetrics(
            cpu_usage_percent=cpu_percent,
            memory_usage_percent=memory.percent,
            disk_usage_percent=disk.percent,
            uptime_seconds=time.time() - app_start_time
        )
    except Exception as e:
        logger.warning(f"Failed to get system metrics: {e}")
        return SystemMetrics(uptime_seconds=time.time() - app_start_time)

# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": settings.app_name, 
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "disabled",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Determine overall status
        health_status = HealthStatus.HEALTHY
        checks_passed = 0
        checks_total = 2
        
        # Check AI model
        model_status = ModelStatus(
            loaded=ai_model_loaded,
            model_name=settings.model_name if ai_model_loaded else None,
            model_path=settings.model_path if ai_model_loaded else None,
            last_inference_time=datetime.utcnow() if ai_model_loaded else None
        )
        if ai_model_loaded:
            checks_passed += 1
        else:
            health_status = HealthStatus.DEGRADED
        
        # Get system metrics
        system_metrics = get_system_metrics()
        checks_passed += 1
        
        # Additional health details
        details = {
            "kubernetes_ready": True,
            "environment": settings.environment,
            "debug_mode": settings.debug
        }
        
        return HealthResponse(
            status=health_status,
            timestamp=datetime.utcnow(),
            version=settings.app_version,
            environment=settings.environment,
            model_status=model_status,
            system_metrics=system_metrics,
            checks_passed=checks_passed,
            checks_total=checks_total,
            details=details
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status=HealthStatus.UNHEALTHY,
            timestamp=datetime.utcnow(),
            version=settings.app_version,
            environment=settings.environment,
            model_status=ModelStatus(loaded=False),
            system_metrics=SystemMetrics(uptime_seconds=time.time() - app_start_time),
            checks_passed=0,
            checks_total=2
        )

@app.get("/health/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check():
    """Kubernetes readiness probe endpoint"""
    checks = {
        "model_loaded": ai_model_loaded,
        "api_responsive": True,
        "dependencies_available": True  # In production, check database/redis
    }
    
    ready = all(checks.values())
    
    return ReadinessResponse(
        ready=ready,
        timestamp=datetime.utcnow(),
        checks=checks
    )

@app.get("/health/live", response_model=LivenessResponse, tags=["Health"])
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return LivenessResponse(
        alive=True,
        timestamp=datetime.utcnow(),
        uptime_seconds=time.time() - app_start_time
    )

@app.post("/auth/register", response_model=TokenResponse, tags=["Authentication"])
async def register_user(user_data: UserRegister):
    """Register a new user with enhanced validation"""
    # Check if user already exists
    for existing_user in users_db.values():
        if existing_user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user_record = {
        "user_id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "fitness_goals": user_data.fitness_goals,
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow(),
        "is_active": True
    }
    
    users_db[user_id] = user_record
    
    # Initialize conversation history
    conversations_db[user_id] = []
    
    # Generate access token
    access_token = create_access_token({"user_id": user_id, "email": user_data.email})
    
    logger.info(f"New user registered: {user_data.email}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user_id
    )

@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login_user(login_data: UserLogin):
    """User login with enhanced security"""
    # Find user by email
    user = None
    user_id = None
    for uid, user_data in users_db.items():
        if user_data["email"] == login_data.email:
            user = user_data
            user_id = uid
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last active
    user["last_active"] = datetime.utcnow()
    
    # Generate access token
    access_token = create_access_token({"user_id": user_id, "email": user["email"]})
    
    logger.info(f"User logged in: {user['email']}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user_id
    )

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_ai(
    chat_request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Chat with AI fitness assistant - enhanced version"""
    user_id = current_user["user_id"]
    start_time = time.time()
    
    # Generate conversation ID if not provided
    conversation_id = chat_request.conversation_id or str(uuid.uuid4())
    
    # Generate AI response
    try:
        ai_response, tokens_used = generate_ai_response(chat_request.message, chat_request.context)
    except Exception as e:
        logger.error(f"AI response generation failed: {e}")
        raise ModelException("Failed to generate AI response")
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Create conversation record
    conversation_record = {
        "conversation_id": conversation_id,
        "user_message": chat_request.message,
        "ai_response": ai_response,
        "timestamp": datetime.utcnow(),
        "context": chat_request.context,
        "tokens_used": tokens_used,
        "response_time_ms": response_time_ms
    }
    
    # Save to conversation history
    if user_id not in conversations_db:
        conversations_db[user_id] = []
    
    conversations_db[user_id].append(conversation_record)
    
    # Update user's last active time
    current_user["last_active"] = datetime.utcnow()
    
    logger.info(f"Chat response generated for user {user_id}: {tokens_used} tokens, {response_time_ms}ms")
    
    return ChatResponse(
        message=chat_request.message,
        response=ai_response,
        conversation_id=conversation_id,
        timestamp=conversation_record["timestamp"],
        tokens_used=tokens_used,
        response_time_ms=response_time_ms
    )

@app.get("/chat/history/{user_id}", tags=["Chat"])
async def get_conversation_history(
    user_id: str,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get conversation history for a user"""
    # Check if user is requesting their own history or is admin
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Can only access your own conversation history"
        )
    
    # Get conversations for user
    user_conversations = conversations_db.get(user_id, [])
    
    # Apply pagination
    total_conversations = len(user_conversations)
    conversations_slice = user_conversations[offset:offset + limit]
    
    return {
        "user_id": user_id,
        "total_conversations": total_conversations,
        "limit": limit,
        "offset": offset,
        "conversations": conversations_slice
    }

@app.get("/profile", response_model=UserProfile, tags=["User"])
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user's profile"""
    return UserProfile(
        user_id=current_user["user_id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        fitness_goals=current_user.get("fitness_goals"),
        created_at=current_user["created_at"],
        last_active=current_user["last_active"]
    )

@app.put("/profile", tags=["User"])
async def update_user_profile(
    profile_update: UpdateProfile,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile with validation"""
    user_id = current_user["user_id"]
    
    # Update fields if provided
    if profile_update.first_name is not None:
        users_db[user_id]["first_name"] = profile_update.first_name
    if profile_update.last_name is not None:
        users_db[user_id]["last_name"] = profile_update.last_name
    if profile_update.fitness_goals is not None:
        users_db[user_id]["fitness_goals"] = profile_update.fitness_goals
    
    users_db[user_id]["last_active"] = datetime.utcnow()
    
    logger.info(f"Profile updated for user {user_id}")
    
    return {"message": "Profile updated successfully", "timestamp": datetime.utcnow()}

@app.get("/stats", response_model=UserStats, tags=["Analytics"])
async def get_user_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get comprehensive user statistics"""
    user_id = current_user["user_id"]
    user_conversations = conversations_db.get(user_id, [])
    
    total_conversations = len(user_conversations)
    total_messages = sum(1 for conv in user_conversations)
    
    # Calculate usage over time
    if user_conversations:
        first_conversation = min(conv["timestamp"] for conv in user_conversations)
        days_active = (datetime.utcnow() - first_conversation).days + 1
    else:
        days_active = 0
    
    return UserStats(
        user_id=user_id,
        total_conversations=total_conversations,
        total_messages=total_messages,
        days_active=days_active,
        member_since=current_user["created_at"],
        last_active=current_user["last_active"]
    )

# Application entry point
if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    setup_logging(settings.log_level, json_logs=(settings.environment == "production"))
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level=settings.log_level.lower()
    )