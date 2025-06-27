"""
Chat Agent Service
Orchestrates the interaction between user, LLM and secure database operations
"""
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime
from app.secure_operations import SecureDatabaseOperations, SecureOperationError
from app.llm_integration import OpenRouterClient, UserLLMConfig
import re
from loguru import logger

class OperationMapping:
    """Maps natural language intents to secure operations"""
    
    OPERATION_PATTERNS = {
        # Obras queries
        'get_obras_ativas': [
            r'obras?\s+ativas?',
            r'obras?\s+em\s+andamento',
            r'projetos?\s+ativos?',
            r'obras?\s+andando'
        ],
        'get_obras_todas': [
            r'todas?\s+(?:as\s+)?obras?',
            r'listar?\s+obras?',
            r'minhas?\s+obras?',
            r'todos?\s+(?:os\s+)?projetos?'
        ],
        'get_obras_finalizadas': [
            r'obras?\s+finalizadas?',
            r'obras?\s+conclu[ií]das?',
            r'projetos?\s+finalizados?'
        ],        # Financial queries
        'get_custos_obra': [
            r'custos?\s+(?:da\s+)?obra',
            r'quanto\s+(?:já\s+)?gast[ou|ei]',
            r'valor\s+total\s+(?:da\s+)?obra',
            r'gastos?\s+(?:da\s+)?obra'
        ],
        'get_fornecedores': [
            r'fornecedores?',
            r'listar?\s+fornecedores?',
            r'quais\s+fornecedores?'
        ],
        # Creation operations
        'create_obra': [
            r'criar?\s+(?:uma\s+)?(?:nova\s+)?obra',
            r'adicionar?\s+(?:uma\s+)?(?:nova\s+)?obra',
            r'nova\s+obra',
            r'cadastrar?\s+obra'
        ],
        'create_fornecedor': [
            r'criar?\s+(?:um\s+)?(?:novo\s+)?fornecedor',
            r'adicionar?\s+(?:um\s+)?(?:novo\s+)?fornecedor',
            r'novo\s+fornecedor',
            r'cadastrar?\s+fornecedor'
        ]
    }
    
    @classmethod
    def detect_operation(cls, message: str) -> Optional[str]:
        """Detect which operation the user wants based on message"""
        message_lower = message.lower()
        
        for operation, patterns in cls.OPERATION_PATTERNS.items():            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return operation
        
        return None

class ChatAgent:
    """
    Main chat agent that orchestrates the entire conversation flow
    """
    
    def __init__(self, 
                 db_ops: SecureDatabaseOperations,
                 cache: 'CacheService',
                 user_llm_config: UserLLMConfig):
        self.db_ops = db_ops
        self.cache = cache
        self.llm_client = OpenRouterClient(user_llm_config)
        self.operation_history = []
        
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process user message and return appropriate response
        """
        logger.info(f"Processing message for user {user_id}: {message[:50]}...")
        
        try:
            # 1. Detect operation from message
            operation = OperationMapping.detect_operation(message)
            
            if not operation:
                # Use LLM for complex queries or when no pattern matches
                return await self._handle_complex_query(user_id, message)            
            # 2. Check cache first
            cached_result = await self.cache.get(operation, user_id)
            if cached_result:
                logger.info(f"Returning cached result for {operation}")
                return {
                    "response": self._format_response(operation, cached_result),
                    "operation_performed": operation,
                    "data": cached_result,
                    "from_cache": True
                }
            
            # 3. Execute operation
            result = await self._execute_operation(operation, user_id, message)
            
            # 4. Cache the result
            if result and not isinstance(result, Exception):
                await self.cache.set(operation, user_id, result)
            
            # 5. Format response
            response = self._format_response(operation, result)
            
            # 6. Log operation
            self.operation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "operation": operation,
                "message": message,
                "success": not isinstance(result, Exception)
            })
            
            return {
                "response": response,