"""
OpenRouter LLM Integration Module
Allows users to choose their preferred LLM and use their own API key
"""
import httpx
import json
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
from loguru import logger

class LLMProvider(str, Enum):
    """Supported LLM providers via OpenRouter"""
    GPT_4_TURBO = "openai/gpt-4-turbo-preview"
    GPT_4 = "openai/gpt-4"
    GPT_35_TURBO = "openai/gpt-3.5-turbo"
    CLAUDE_3_OPUS = "anthropic/claude-3-opus"
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet"
    CLAUDE_3_HAIKU = "anthropic/claude-3-haiku"
    GEMINI_PRO = "google/gemini-pro"
    GEMINI_15_PRO = "google/gemini-1.5-pro"
    MIXTRAL_8X7B = "mistralai/mixtral-8x7b"
    LLAMA_3_70B = "meta-llama/llama-3-70b"

class UserLLMConfig(BaseModel):
    """User's LLM configuration"""
    openrouter_api_key: str = Field(..., description="User's OpenRouter API key")
    preferred_model: LLMProvider = Field(default=LLMProvider.GPT_35_TURBO)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2000)
class OpenRouterClient:
    """
    OpenRouter client for LLM interactions
    Implements secure prompt engineering based on Gemini recommendations
    """
    
    def __init__(self, config: UserLLMConfig):
        self.config = config
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://gestao-obras-ai.com",
            "X-Title": "Agente IA Gestão de Obras"
        }
        
    async def create_secure_prompt(self, user_message: str, user_id: str, available_operations: List[str]) -> str:
        """
        Create a secure prompt that prevents SQL injection and ensures data isolation
        """
        system_prompt = f"""Você é um assistente especializado em gestão de obras da construção civil.
        
REGRAS CRÍTICAS DE SEGURANÇA:
1. Você NUNCA gera SQL diretamente
2. Você só pode usar as operações pré-definidas listadas abaixo
3. O user_id '{user_id}' já está automaticamente aplicado em todas as operações
4. NUNCA tente acessar dados de outros usuários
5. Se não houver operação adequada, informe educadamente que não é possível

OPERAÇÕES DISPONÍVEIS:
{chr(10).join(f'- {op}' for op in available_operations)}

FORMATO DE RESPOSTA:
{{
    "operation": "nome_da_operacao",