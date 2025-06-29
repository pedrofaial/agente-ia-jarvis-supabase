# Configuração de Segurança - Fase 1 (MVP)
# Implementação simples usando apenas Supabase Auth

from typing import Optional, Dict
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Inicializar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Security scheme para FastAPI
security = HTTPBearer()

class SimpleAuthSystem:
    """
    Sistema de autenticação simples para MVP.
    Usa apenas Supabase Auth sem complexidade adicional.
    """
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        """
        Valida o token JWT do Supabase e retorna os dados do usuário.
        """
        token = credentials.credentials
        
        try:
            # Validar token com Supabase
            user_response = supabase.auth.get_user(token)
            
            if not user_response or not user_response.user:
                raise HTTPException(
                    status_code=401,
                    detail="Token inválido ou expirado"
                )
            
            user = user_response.user
            
            # Log de acesso (básico)
            logger.info(f"Acesso autorizado - User ID: {user.id}")
            
            return {
                "id": user.id,
                "email": user.email,
                "metadata": user.user_metadata
            }
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Falha na autenticação"
            )
    
    @staticmethod
    async def login(email: str, password: str) -> Dict:
        """
        Realiza login usando Supabase Auth.
        """
        try:
            # Login com Supabase
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.session:
                raise HTTPException(
                    status_code=401,
                    detail="Credenciais inválidas"
                )
            
            logger.info(f"Login bem-sucedido - Email: {email}")
            
            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no login: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Falha no login"
            )
    
    @staticmethod
    async def logout(token: str) -> Dict:
        """
        Realiza logout invalidando o token no Supabase.
        """
        try:
            # Logout no Supabase
            supabase.auth.sign_out()
            
            logger.info("Logout realizado com sucesso")
            
            return {"message": "Logout realizado com sucesso"}
            
        except Exception as e:
            logger.error(f"Erro no logout: {str(e)}")
            return {"message": "Logout realizado (com avisos)"}
    
    @staticmethod
    async def refresh_token(refresh_token: str) -> Dict:
        """
        Renova o token de acesso usando o refresh token.
        """
        try:
            # Renovar token com Supabase
            auth_response = supabase.auth.refresh_session(refresh_token)
            
            if not auth_response.session:
                raise HTTPException(
                    status_code=401,
                    detail="Refresh token inválido"
                )
            
            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "token_type": "bearer",
                "expires_in": 3600
            }
            
        except Exception as e:
            logger.error(f"Erro ao renovar token: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Falha ao renovar token"
            )

# Criar instância global
auth = SimpleAuthSystem()

# Dependency para usar nas rotas
async def require_auth(user: Dict = Depends(auth.get_current_user)) -> Dict:
    """
    Dependency que requer autenticação.
    Uso: user = Depends(require_auth)
    """
    return user

# Exemplo de uso em rotas:
"""
from fastapi import FastAPI, Depends
from auth_phase1 import auth, require_auth

app = FastAPI()

@app.post("/login")
async def login(email: str, password: str):
    return await auth.login(email, password)

@app.get("/protected")
async def protected_route(user = Depends(require_auth)):
    return {"message": f"Olá {user['email']}!"}
"""
