"""
Main FastAPI Application
Implements secure architecture based on Gemini 2.0 Pro analysis
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from jose import jwt, JWTError
from datetime import datetime, timedelta
import redis.asyncio as redis
from loguru import logger
from contextlib import asynccontextmanager

# Import our modules
from app.secure_operations import SecureDatabaseOperations, ObraCreate
from app.llm_integration import OpenRouterClient, UserLLMConfig, LLMProvider

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")
# Redis client for caching
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global redis_client
    # Startup
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Connected to Redis")
    yield
    # Shutdown
    await redis_client.close()
    logger.info("Disconnected from Redis")

# Initialize FastAPI app
app = FastAPI(
    title="Agente IA Gestão de Obras API",
    description="API segura para gestão de obras com IA",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Security
security = HTTPBearer()

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Pydantic models
class UserLogin(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6)

class LLMConfigRequest(BaseModel):
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    preferred_model: LLMProvider = Field(default=LLMProvider.GPT_35_TURBO)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class ChatMessage(BaseModel):
    message: str = Field(..., description="User message")

class ChatResponse(BaseModel):
    response: str
    operation_performed: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Validate JWT token and return user info"""
    token = credentials.credentials
    try: