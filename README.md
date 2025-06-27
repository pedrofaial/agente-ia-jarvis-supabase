# 🏗️ Agente IA para Gestão de Obras

Sistema inteligente de gestão de obras da construção civil com interface de chat em linguagem natural, desenvolvido com as melhores práticas de segurança e escalabilidade.

## 📋 Características Principais

- 🤖 **Chat com IA**: Interface conversacional em português
- 🔐 **Segurança Multicamadas**: JWT + RLS + Validação de operações
- 🚀 **Alta Performance**: Cache Redis + Otimização de queries
- 📊 **Analytics e Insights**: Relatórios e análises inteligentes
- 🔄 **Multi-LLM**: Suporte para múltiplos modelos via OpenRouter
- 📈 **Monitoramento**: Prometheus + Grafana para métricas

## 🏛️ Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Supabase   │
│   (React)   │     │  (FastAPI)  │     │ (PostgreSQL)│
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │ OpenRouter  │
                    │    (LLM)    │
                    └─────────────┘
```

## 🚀 Início Rápido

### Pré-requisitos
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- Conta no Supabase
- Chave API do OpenRouter

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/agente-ia-gestao-obras.git
cd agente-ia-gestao-obras
```

### 2. Configure as Variáveis de Ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### 3. Inicie com Docker Compose

```bash
docker-compose up -d
```

### 4. Instale as Dependências

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bashcd frontend
npm install
```

### 5. Execute a Aplicação

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Acesse: http://localhost:5173

## 🔧 Configuração do Supabase

1. Crie um projeto no [Supabase](https://supabase.com)
2. Execute as migrations do banco (pasta `/database/migrations`)
3. Configure as políticas RLS
4. Copie as chaves API para o arquivo `.env`

## 🤖 Configuração do OpenRouter

1. Crie uma conta no [OpenRouter](https://openrouter.ai)
2. Gere sua chave API
3. O usuário configurará no frontend ao fazer login

## 📚 Documentação da API

### Autenticação

```http
POST /api/auth/login
Content-Type: application/json

{