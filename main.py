"""
Simple Production FastAPI Application for AI Fitness Assistant
Compatible with current environment - no complex imports
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import hashlib
import jwt
import os
import uuid
import time
from typing import Optional, List, Dict, Any

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-test-secret-key-for-jwt-tokens")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Database simulation
users_db: Dict[str, Dict[str, Any]] = {}
conversations_db: Dict[str, List[Dict[str, Any]]] = {}

# Security
security = HTTPBearer()

# Global state
app_start_time = time.time()
ai_model_loaded = False

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    fitness_goals: Optional[str] = Field(None, max_length=500)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    response: str
    conversation_id: str
    timestamp: datetime
    tokens_used: int
    response_time_ms: Optional[int] = None

class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    fitness_goals: Optional[str]
    created_at: datetime
    last_active: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    model_loaded: bool
    version: str
    environment: str
    uptime_seconds: float
    checks_passed: int
    checks_total: int

# App lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    global ai_model_loaded
    print("🚀 Starting AI Fitness API...")
    ai_model_loaded = True
    print("✅ AI Model loaded successfully (mock mode)")
    yield
    print("🔄 Shutting down AI Fitness API...")

# FastAPI App
app = FastAPI(
    title="AI Fitness Assistant API",
    description="Production-ready API for AI-powered fitness coaching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility Functions
def hash_password(password: str) -> str:
    salt = "fitness-app-salt"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

def get_current_user(user_id: str = Depends(verify_token)) -> Dict[str, Any]:
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def generate_ai_response(message: str, context: Optional[Dict[str, Any]] = None) -> tuple[str, int]:
    """Enhanced AI response generator"""
    fitness_responses = {
        "workout": "🏋️ Here's your personalized workout: Start with 10min dynamic warm-up, then 3 sets of: squats (12 reps), push-ups (10 reps), lunges (10/leg), plank (30s). Cool down with stretching!",
        "nutrition": "🥗 Nutrition guide: Aim for 1.6-2.2g protein/kg body weight, complex carbs from whole grains, healthy fats (nuts/avocado), 5-9 servings fruits/veggies daily. Stay hydrated!",
        "motivation": "💪 You've got this! Progress isn't linear - every workout and healthy choice builds momentum. Consistency beats perfection. Celebrate small wins along your fitness journey!",
        "recovery": "😴 Recovery is key: 7-9hrs quality sleep, include rest days, try gentle yoga/walking for active recovery. Listen to your body's signals!",
        "cardio": "❤️ Cardio mix: Combine steady-state (20-30min moderate) with HIIT (15-20min intervals). Start 3x/week, find activities you enjoy - dancing, swimming, hiking!",
        "strength": "🔥 Strength training: Focus on compound movements (deadlifts, squats, bench press), 2-3x/week, progressive overload, proper form over heavy weights!",
        "flexibility": "🧘 Flexibility routine: Daily 10-15min stretching, focus on tight areas (hips, shoulders, hamstrings), yoga 1-2x/week, stretch after workouts!",
    }
    
    message_lower = message.lower()
    for key, response in fitness_responses.items():
        if key in message_lower:
            return response, len(response.split())
    
    # Default personalized response
    response = f"🤖 As your AI fitness coach, I'm here to help with: {message}. I can assist with workout plans, nutrition advice, motivation, recovery tips, cardio routines, strength training, and flexibility! What would you like to focus on?"
    return response, len(response.split())

# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI Fitness Assistant API",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    uptime = time.time() - app_start_time
    status_val = "healthy" if ai_model_loaded else "degraded"
    
    return HealthResponse(
        status=status_val,
        timestamp=datetime.utcnow(),
        model_loaded=ai_model_loaded,
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development"),
        uptime_seconds=uptime,
        checks_passed=2 if ai_model_loaded else 1,
        checks_total=2
    )

@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    return {
        "ready": ai_model_loaded,
        "timestamp": datetime.utcnow(),
        "checks": {
            "model_loaded": ai_model_loaded,
            "api_responsive": True
        }
    }

@app.get("/health/live", tags=["Health"])
async def liveness_check():
    return {
        "alive": True,
        "timestamp": datetime.utcnow(),
        "uptime_seconds": time.time() - app_start_time
    }

@app.post("/auth/register", tags=["Authentication"])
async def register_user(user_data: UserRegister):
    # Check if user exists
    for existing_user in users_db.values():
        if existing_user["email"] == user_data.email:
            raise HTTPException(status_code=409, detail="User already exists")
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    users_db[user_id] = {
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
    
    conversations_db[user_id] = []
    access_token = create_access_token({"user_id": user_id, "email": user_data.email})
    
    return {
        "message": "User registered successfully",
        "user_id": user_id,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/login", tags=["Authentication"])
async def login_user(login_data: UserLogin):
    user = None
    user_id = None
    
    for uid, user_data in users_db.items():
        if user_data["email"] == login_data.email:
            user = user_data
            user_id = uid
            break
    
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user["last_active"] = datetime.utcnow()
    access_token = create_access_token({"user_id": user_id, "email": user["email"]})
    
    return {
        "message": "Login successful",
        "user_id": user_id,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_ai(
    chat_request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    start_time = time.time()
    
    conversation_id = chat_request.conversation_id or str(uuid.uuid4())
    ai_response, tokens_used = generate_ai_response(chat_request.message, chat_request.context)
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Save conversation
    conversation_record = {
        "conversation_id": conversation_id,
        "user_message": chat_request.message,
        "ai_response": ai_response,
        "timestamp": datetime.utcnow(),
        "context": chat_request.context,
        "tokens_used": tokens_used,
        "response_time_ms": response_time_ms
    }
    
    if user_id not in conversations_db:
        conversations_db[user_id] = []
    conversations_db[user_id].append(conversation_record)
    
    current_user["last_active"] = datetime.utcnow()
    
    return ChatResponse(
        message=chat_request.message,
        response=ai_response,
        conversation_id=conversation_id,
        timestamp=conversation_record["timestamp"],
        tokens_used=tokens_used,
        response_time_ms=response_time_ms
    )

@app.get("/profile", response_model=UserProfile, tags=["User"])
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return UserProfile(
        user_id=current_user["user_id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        fitness_goals=current_user.get("fitness_goals"),
        created_at=current_user["created_at"],
        last_active=current_user["last_active"]
    )

@app.get("/chat/history/{user_id}", tags=["Chat"])
async def get_conversation_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user_conversations = conversations_db.get(user_id, [])
    total = len(user_conversations)
    conversations_slice = user_conversations[offset:offset + limit]
    
    return {
        "user_id": user_id,
        "total_conversations": total,
        "limit": limit,
        "offset": offset,
        "conversations": conversations_slice
    }

@app.get("/stats", tags=["Analytics"])
async def get_user_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["user_id"]
    user_conversations = conversations_db.get(user_id, [])
    
    total_conversations = len(user_conversations)
    total_messages = len(user_conversations)
    days_active = 0
    
    if user_conversations:
        first_conversation = min(conv["timestamp"] for conv in user_conversations)
        days_active = (datetime.utcnow() - first_conversation).days + 1
    
    return {
        "user_id": user_id,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "days_active": days_active,
        "member_since": current_user["created_at"],
        "last_active": current_user["last_active"]
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting AI Fitness Assistant API v1.0.0")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)