# Sistema de Roteamento Inteligente de LLM

from enum import Enum
from typing import Dict, List, Optional
import re

class LLMModel(Enum):
    """Modelos disponíveis no OpenRouter com seus custos"""
    # Modelos Econômicos (< $0.001 por 1k tokens)
    GEMINI_FLASH = "google/gemini-flash-1.5"  # $0.00025/1k - Rápido e barato
    LLAMA_3_8B = "meta-llama/llama-3-8b"      # $0.00018/1k - Muito econômico
    
    # Modelos Intermediários ($0.001-0.01 por 1k tokens)
    CLAUDE_HAIKU = "anthropic/claude-3-haiku"  # $0.0025/1k - Bom custo-benefício
    GPT_3_5 = "openai/gpt-3.5-turbo"          # $0.002/1k - Versátil
    
    # Modelos Premium (> $0.01 por 1k tokens)
    CLAUDE_SONNET = "anthropic/claude-3-sonnet" # $0.015/1k - Alta qualidade
    GPT_4 = "openai/gpt-4-turbo"               # $0.03/1k - Máxima capacidade
    CLAUDE_OPUS = "anthropic/claude-3-opus"     # $0.075/1k - Top de linha

class QueryComplexity(Enum):
    """Níveis de complexidade das queries"""
    SIMPLE = "simple"        # Consultas diretas
    MODERATE = "moderate"    # Análises básicas
    COMPLEX = "complex"      # Múltiplas tabelas, cálculos
    CREATIVE = "creative"    # Geração de relatórios, insights

class LLMRouter:
    """Roteador inteligente para seleção de modelo LLM"""
    
    def __init__(self):
        # Padrões para identificar complexidade
        self.simple_patterns = [
            r"listar?",
            r"mostrar?",
            r"quais são",
            r"quantos?",
            r"status de",
            r"informações sobre"
        ]
        
        self.moderate_patterns = [
            r"analis[ae]r?",
            r"calcular?",
            r"total de",
            r"média de",
            r"resumo de",
            r"comparar?"
        ]
        
        self.complex_patterns = [
            r"relatório",
            r"dashboard",
            r"projeção",
            r"tendência",
            r"otimizar?",
            r"sugerir?",
            r"melhor estratégia"
        ]
        
        # Mapeamento de complexidade para modelo
        self.complexity_model_map = {
            QueryComplexity.SIMPLE: LLMModel.GEMINI_FLASH,
            QueryComplexity.MODERATE: LLMModel.CLAUDE_HAIKU,
            QueryComplexity.COMPLEX: LLMModel.CLAUDE_SONNET,
            QueryComplexity.CREATIVE: LLMModel.GPT_4
        }
    
    def analyze_query(self, query: str) -> Dict:
        """Analisa a query e retorna complexidade e modelo recomendado"""
        query_lower = query.lower()
        
        # Verifica se é query SQL direta (sem LLM)
        if self._is_direct_query(query_lower):
            return {
                "needs_llm": False,
                "complexity": QueryComplexity.SIMPLE,
                "reason": "Query padrão - SQL direto"
            }
        
        # Determina complexidade
        complexity = self._determine_complexity(query_lower)
        
        # Seleciona modelo baseado na complexidade
        model = self.complexity_model_map[complexity]
        
        # Override para economizar em produção
        if self._can_use_cheaper_model(query_lower, complexity):
            model = LLMModel.GEMINI_FLASH
            
        return {
            "needs_llm": True,
            "complexity": complexity,
            "model": model,
            "estimated_tokens": self._estimate_tokens(query),
            "estimated_cost": self._estimate_cost(model, query),
            "reason": self._get_reason(complexity)
        }
    
    def _is_direct_query(self, query: str) -> bool:
        """Verifica se a query pode ser respondida sem LLM"""
        direct_queries = [
            "obras ativas",
            "fornecedores ativos",
            "total de gastos",
            "lançamentos pendentes",
            "obras concluídas"
        ]
        
        return any(dq in query for dq in direct_queries)
    
    def _determine_complexity(self, query: str) -> QueryComplexity:
        """Determina a complexidade da query"""
        # Verifica padrões complexos primeiro
        for pattern in self.complex_patterns:
            if re.search(pattern, query):
                return QueryComplexity.COMPLEX
        
        # Depois moderados
        for pattern in self.moderate_patterns:
            if re.search(pattern, query):
                return QueryComplexity.MODERATE
        
        # Por fim, simples
        for pattern in self.simple_patterns:
            if re.search(pattern, query):
                return QueryComplexity.SIMPLE
        
        # Default para moderado se não identificar
        return QueryComplexity.MODERATE
    
    def _can_use_cheaper_model(self, query: str, complexity: QueryComplexity) -> bool:
        """Verifica se pode usar um modelo mais barato"""
        # Se tem function no banco que resolve, usa modelo barato
        function_keywords = [
            "dashboard", "resumo", "fluxo de caixa", 
            "comparar obras", "top fornecedores"
        ]
        
        return any(keyword in query for keyword in function_keywords)
    
    def _estimate_tokens(self, query: str) -> int:
        """Estima número de tokens (aproximado)"""
        # Regra simples: ~1.3 tokens por palavra em português
        words = len(query.split())
        # Adiciona overhead do contexto do sistema
        return int(words * 1.3) + 500
    
    def _estimate_cost(self, model: LLMModel, query: str) -> float:
        """Estima custo em USD"""
        tokens = self._estimate_tokens(query)
        
        # Custos por 1k tokens (input + output estimado)
        costs = {
            LLMModel.GEMINI_FLASH: 0.00025,
            LLMModel.LLAMA_3_8B: 0.00018,
            LLMModel.CLAUDE_HAIKU: 0.0025,
            LLMModel.GPT_3_5: 0.002,
            LLMModel.CLAUDE_SONNET: 0.015,
            LLMModel.GPT_4: 0.03,
            LLMModel.CLAUDE_OPUS: 0.075
        }
        
        cost_per_token = costs.get(model, 0.01) / 1000
        return tokens * cost_per_token * 2  # x2 para input+output
    
    def _get_reason(self, complexity: QueryComplexity) -> str:
        """Retorna explicação da escolha"""
        reasons = {
            QueryComplexity.SIMPLE: "Consulta simples - modelo econômico",
            QueryComplexity.MODERATE: "Análise moderada - modelo balanceado",
            QueryComplexity.COMPLEX: "Query complexa - modelo avançado",
            QueryComplexity.CREATIVE: "Geração criativa - modelo premium"
        }
        return reasons[complexity]
