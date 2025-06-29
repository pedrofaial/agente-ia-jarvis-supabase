# Arquitetura de Segurança Híbrida Avançada
# Combina JWT do Supabase com tokens de sessão próprios

from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import secrets
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
from supabase import create_client
import hashlib
import json

class SecureAuthSystem:
    """Sistema de autenticação com múltiplas camadas de segurança"""
    
    def __init__(self, supabase_url: str, supabase_key: str, 
                 jwt_secret: str, redis_client: redis.Redis):
        self.supabase = create_client(supabase_url, supabase_key)
        self.jwt_secret = jwt_secret
        self.redis = redis_client
        self.security = HTTPBearer()
        
        # Configurações de segurança
        self.SESSION_DURATION = 3600  # 1 hora
        self.REFRESH_THRESHOLD = 300  # 5 minutos
        self.MAX_SESSIONS_PER_USER = 5
        self.RATE_LIMIT_REQUESTS = 100  # por hora
