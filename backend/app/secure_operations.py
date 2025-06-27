"""
Secure Database Operations Module
Implements secure API calls instead of direct SQL generation
Based on Gemini 2.0 Pro recommendations
"""
from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import date, datetime
from supabase import Client
from pydantic import BaseModel, validator
import re

class SecureOperationError(Exception):
    """Custom exception for secure operations"""
    pass

class ObraCreate(BaseModel):
    nome: str
    responsavel: str
    cliente: Optional[str] = None
    status: str = "Em andamento"
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    endereco: Optional[str] = None
    tamanho_obra: Optional[str] = None
    tamanho_terreno: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        allowed = ['Em andamento', 'Paralisada', 'Finalizada']
        if v not in allowed:
            raise ValueError(f'Status deve ser um de: {allowed}')
        return v
class SecureDatabaseOperations:
    """
    Secure database operations class
    All operations are pre-defined and validated
    No direct SQL execution from LLM
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        
    # ============= OBRAS OPERATIONS =============
    
    async def get_obras_by_status(self, user_id: str, status: str) -> List[Dict]:
        """Get obras filtered by status for a specific user"""
        try:
            result = self.client.table('obras') \
                .select('*') \
                .eq('user_id', user_id) \
                .eq('status', status) \
                .execute()
            return result.data
        except Exception as e:
            raise SecureOperationError(f"Erro ao buscar obras: {str(e)}")
    
    async def get_all_obras(self, user_id: str) -> List[Dict]:
        """Get all obras for a specific user"""
        try:
            result = self.client.table('obras') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('created_at', desc=True) \
                .execute()
            return result.data        except Exception as e:
            raise SecureOperationError(f"Erro ao buscar todas as obras: {str(e)}")
    
    async def create_obra(self, user_id: str, obra_data: ObraCreate) -> Dict:
        """Create a new obra with validation"""
        try:
            data = obra_data.dict()
            data['user_id'] = user_id
            result = self.client.table('obras').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise SecureOperationError(f"Erro ao criar obra: {str(e)}")
    
    async def update_obra_status(self, user_id: str, obra_id: str, new_status: str) -> Dict:
        """Update obra status with validation"""
        allowed_status = ['Em andamento', 'Paralisada', 'Finalizada']
        if new_status not in allowed_status:
            raise SecureOperationError(f"Status inválido: {new_status}")
        
        try:
            result = self.client.table('obras') \
                .update({'status': new_status, 'updated_at': datetime.now().isoformat()}) \
                .eq('id', obra_id) \
                .eq('user_id', user_id) \
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise SecureOperationError(f"Erro ao atualizar status: {str(e)}")
    
    # ============= FINANCIAL OPERATIONS =============