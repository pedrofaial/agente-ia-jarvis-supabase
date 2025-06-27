"""
Monitoring and Logging Service
Implements comprehensive monitoring based on Gemini recommendations
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from loguru import logger
import sys
from datetime import datetime
from typing import Dict, Any
import json

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

# Prometheus metrics
request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)
request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

llm_request_count = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'status']
)

llm_tokens_used = Counter(
    'llm_tokens_total',
    'Total tokens used by LLM',
    ['model', 'type']  # type: prompt or completion
)

cache_operations = Counter(
    'cache_operations_total',
    'Cache operations',
    ['operation', 'result']  # operation: get/set, result: hit/miss/error
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

database_operations = Counter(
    'database_operations_total',
    'Database operations',
    ['operation', 'table', 'status']
)