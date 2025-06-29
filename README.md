# 🏗️ Agente IA Jarvis + Supabase

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
git clone https://github.com/pedrofaial/agente-ia-jarvis-supabase.git
cd agente-ia-jarvis-supabase
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
```bash
cd frontend
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
  "email": "usuario@exemplo.com",
  "password": "senha123"
}
```

### Chat

```http
POST /api/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "Mostre minhas obras ativas",
  "context": {
    "obra_id": "uuid-opcional",
    "openrouter_key": "sk-or-v1-..."
  }
}
```

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais:

- **obras**: Informações gerais das obras
- **lancamentos_financeiros**: Registros financeiros
- **itens_orcamento**: Detalhes do orçamento
- **fases_obra**: Fases de cada obra
- **tipos_insumo**: Tipos de materiais/serviços
- **fornecedores**: Cadastro de fornecedores

Todas as tabelas implementam RLS (Row Level Security) para garantir isolamento de dados por usuário.

## 🛡️ Segurança

### Implementação Atual (Fase 1 - MVP)
- **RLS (Row Level Security)**: Isolamento de dados por usuário
- **JWT do Supabase**: Autenticação gerenciada
- **HTTPS**: Obrigatório em todas as comunicações
- **Validação básica**: Proteção contra injeções

### Roadmap de Segurança
Estamos seguindo uma estratégia evolutiva de segurança:
- **Fase 1 (Atual)**: Autenticação Supabase básica ✅
- **Fase 2**: Sistema híbrido com cache e rate limiting 🔄
- **Fase 3**: Segurança enterprise com 2FA e auditoria completa 📅

📄 **[Ver estratégia completa de segurança](docs/SECURITY_STRATEGY.md)**

## 📈 Monitoramento

- **Prometheus**: Coleta de métricas
- **Grafana**: Visualização de dashboards
- **Logs estruturados**: JSON com níveis configuráveis

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Pedro Faial** - *Desenvolvimento inicial* - [pedrofaial](https://github.com/pedrofaial)

## 🙏 Agradecimentos

- Equipe Supabase pela excelente plataforma
- OpenRouter pela integração com múltiplos LLMs
- Comunidade open source pelos frameworks utilizados
