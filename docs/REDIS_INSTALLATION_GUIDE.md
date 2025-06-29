# 📦 Guia de Instalação e Configuração do Redis

## 🔴 O que é o Redis?

Redis é um banco de dados em memória (RAM) ultra-rápido, usado como:
- **Cache**: Armazena dados temporários para acelerar o sistema
- **Session Store**: Guarda sessões de usuários
- **Rate Limiting**: Controla limite de requisições
- **Fila**: Processamento assíncrono de tarefas

## 📋 Instalação por Sistema Operacional

### 🪟 Windows (Desenvolvimento)

#### Opção 1: Redis via WSL2 (Recomendado)
```bash
# 1. Instalar WSL2 (se ainda não tiver)
wsl --install

# 2. Dentro do WSL2 (Ubuntu)
sudo apt update
sudo apt install redis-server

# 3. Iniciar o Redis
sudo service redis-server start

# 4. Verificar se está funcionando
redis-cli ping
# Deve retornar: PONG
```

#### Opção 2: Redis Windows (Memurai)
```powershell
# 1. Baixar Memurai (Redis para Windows)
# https://www.memurai.com/get-memurai

# 2. Instalar o .msi baixado

# 3. O serviço inicia automaticamente
# Porta padrão: 6379
```

#### Opção 3: Docker (Mais Fácil)
```bash
# 1. Com Docker instalado, execute:
docker run -d -p 6379:6379 --name redis-dev redis:alpine

# 2. Para parar/iniciar
docker stop redis-dev
docker start redis-dev
```

### 🐧 Linux (Ubuntu/Debian)
```bash
# 1. Atualizar pacotes
sudo apt update

# 2. Instalar Redis
sudo apt install redis-server

# 3. Configurar para iniciar com o sistema
sudo systemctl enable redis-server

# 4. Iniciar o serviço
sudo systemctl start redis-server

# 5. Verificar status
sudo systemctl status redis-server
```

### 🍎 macOS
```bash
# 1. Com Homebrew
brew install redis

# 2. Iniciar como serviço
brew services start redis

# 3. Ou iniciar manualmente
redis-server
```

## 🔧 Configuração Básica

### 1. Arquivo de Configuração
```bash
# Linux/WSL
sudo nano /etc/redis/redis.conf

# Windows (Memurai)
# C:\Program Files\Memurai\redis.conf
```

### 2. Configurações Importantes para Desenvolvimento
```conf
# Porta (padrão: 6379)
port 6379

# Bind (aceitar conexões)
bind 127.0.0.1 ::1

# Senha (opcional para dev, obrigatório para produção)
# requirepass suaSenhaSegura123

# Persistência (opcional)
save 900 1
save 300 10
save 60 10000

# Limite de memória
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## 🐳 Docker Compose (Recomendado para o Projeto)

Já temos o Redis configurado no `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:alpine
    container_name: redis-gestao-obras
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis-data:
```

### Comandos Docker Compose:
```bash
# Iniciar apenas o Redis
docker-compose up -d redis

# Ver logs
docker-compose logs redis

# Parar
docker-compose stop redis

# Remover (cuidado, apaga dados)
docker-compose down -v
```

## 🧪 Testando a Instalação

### 1. Via Redis CLI
```bash
# Conectar ao Redis
redis-cli

# Comandos de teste
127.0.0.1:6379> ping
PONG

127.0.0.1:6379> set teste "Hello Redis"
OK

127.0.0.1:6379> get teste
"Hello Redis"

127.0.0.1:6379> del teste
(integer) 1

127.0.0.1:6379> exit
```

### 2. Via Python
```python
# Instalar cliente Python
pip install redis

# Testar conexão
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
print(r.ping())  # True

# Operações básicas
r.set('nome', 'João')
print(r.get('nome'))  # João

# Com expiração (TTL)
r.setex('token', 3600, 'abc123')  # Expira em 1 hora
```

## 🔌 Integração com o Projeto

### 1. Configuração no `.env`
```env
# Redis Configuration
REDIS_URL=redis://localhost:6379
# Com senha (produção)
# REDIS_URL=redis://:suaSenhaSegura123@localhost:6379
```

### 2. Cliente Redis para FastAPI
```python
# backend/app/core/redis_client.py
import redis
from redis import Redis
import os
from typing import Optional

class RedisClient:
    _instance: Optional[Redis] = None
    
    @classmethod
    def get_instance(cls) -> Redis:
        if cls._instance is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            cls._instance = redis.from_url(
                redis_url,
                decode_responses=True,
                health_check_interval=30
            )
        return cls._instance
    
    @classmethod
    def close(cls):
        if cls._instance:
            cls._instance.close()
            cls._instance = None

# Função helper para dependency injection
def get_redis() -> Redis:
    return RedisClient.get_instance()
```

### 3. Uso em Rotas FastAPI
```python
from fastapi import Depends
from redis import Redis
from app.core.redis_client import get_redis

@app.get("/cache-example")
async def cache_example(redis: Redis = Depends(get_redis)):
    # Verificar cache
    cached = redis.get("my_data")
    if cached:
        return {"data": cached, "from_cache": True}
    
    # Processar dados (simulado)
    data = "Dados processados"
    
    # Salvar no cache por 5 minutos
    redis.setex("my_data", 300, data)
    
    return {"data": data, "from_cache": False}
```

## 📊 Monitoramento

### 1. Redis CLI Monitor
```bash
# Ver comandos em tempo real
redis-cli monitor

# Ver informações do servidor
redis-cli info

# Ver uso de memória
redis-cli info memory
```

### 2. RedisInsight (GUI)
```bash
# Download: https://redis.com/redisinsight/

# Ou via Docker
docker run -d -p 8001:8001 --name redisinsight redislabs/redisinsight
# Acesse: http://localhost:8001
```

## 🚨 Troubleshooting

### Problema 1: "Connection refused"
```bash
# Verificar se o Redis está rodando
ps aux | grep redis

# Linux: Reiniciar serviço
sudo systemctl restart redis-server

# Docker: Verificar container
docker ps
docker start redis-dev
```

### Problema 2: "MISCONF Redis is configured to save RDB snapshots"
```bash
# Dar permissão na pasta de dados
sudo chown redis:redis /var/lib/redis
sudo chmod 755 /var/lib/redis
```

### Problema 3: Memória cheia
```bash
# Ver uso de memória
redis-cli info memory

# Limpar tudo (CUIDADO!)
redis-cli FLUSHALL

# Ou configurar política de eviction
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 🔒 Segurança (Importante para Produção)

### 1. Definir Senha
```bash
# No redis.conf
requirepass SuaSenhaForte123!

# Ou via comando
redis-cli CONFIG SET requirepass SuaSenhaForte123!
```

### 2. Desabilitar Comandos Perigosos
```conf
# No redis.conf
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

### 3. Limitar Acesso
```conf
# Apenas localhost
bind 127.0.0.1 ::1

# Firewall (Ubuntu)
sudo ufw allow from 192.168.1.0/24 to any port 6379
```

## 📈 Quando Usar Redis no Projeto

### ✅ Use para:
1. **Cache de queries pesadas** (dashboard, relatórios)
2. **Sessões de usuário** (Fase 2)
3. **Rate limiting** (evitar spam)
4. **Filas de processamento** (emails, notificações)
5. **Contadores** (visualizações, acessos)

### ❌ NÃO use para:
1. Dados permanentes críticos
2. Arquivos grandes (> 512MB)
3. Dados que precisam de transações complexas

## 🎯 Próximos Passos

1. **Desenvolvimento**: Use Docker Compose
2. **Testes**: Redis local ou WSL2
3. **Produção**: Redis Cloud ou AWS ElastiCache

---

**Nota**: Para a Fase 1 (MVP), o Redis é OPCIONAL. Implemente apenas quando precisar de cache ou na transição para Fase 2.
