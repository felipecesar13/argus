# Code Review Assistant

Um sistema de revisão de código automatizado com múltiplos agentes especializados. Você submete um diff de PR e o sistema analisa paralelamente segurança, performance e estilo — exibindo os comentários em tempo real no browser.

---

## Stack

| Camada         | Tecnologia            | Papel                                                   |
| -------------- | --------------------- | ------------------------------------------------------- |
| Frontend       | Angular               | UI de diff viewer e painel de comentários em tempo real |
| API            | NestJS                | Gateway, autenticação, filas e orquestração SSE         |
| Agent          | LangGraph + LangChain | Grafo de agentes revisores em paralelo                  |
| Diff Processor | Go                    | Parser de unified diff de alta performance              |
| Banco de dados | PostgreSQL            | Persistência de reviews e comentários                   |
| Cache / Filas  | Redis                 | Cache de resultados e filas BullMQ                      |

---

## Arquitetura

```
Angular
  │
  │  POST /reviews  (diff bruto)
  ▼
NestJS API
  │
  ├──► Go Diff Processor  ──►  []FileDiff (parse e normalização)
  │
  └──► LangGraph Agent
          │
          ├── security_reviewer  ─┐
          ├── performance_reviewer─┼──► aggregator ──► SSE stream
          └── style_reviewer     ─┘
                │
                ▼
          NestJS  ──►  SSE  ──►  Angular
```

### Fluxo completo

1. Dev cola o diff no Angular e submete
2. Angular envia `POST /reviews` para o NestJS
3. NestJS chama o serviço Go (`POST /parse`) que normaliza o diff em `[]FileDiff`
4. NestJS envia o `[]FileDiff` para o agente Python via HTTP
5. LangGraph executa os três reviewers em paralelo
6. Cada reviewer streama comentários de volta ao NestJS via SSE
7. NestJS repassa o stream para o Angular via SSE
8. Angular renderiza os comentários em tempo real, separados por categoria

---

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose
- [Node.js](https://nodejs.org/) 20+
- [Go](https://go.dev/) 1.22+
- [Python](https://www.python.org/) 3.11+
- Chave de API da OpenAI ou Anthropic (configurada no `.env`)

---

## Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/code-review-assistant.git
cd code-review-assistant
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e preencha ao menos:

```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/reviews
REDIS_URL=redis://localhost:6379
JWT_SECRET=sua-chave-secreta
```

### 3. Suba os serviços com Docker Compose

```bash
docker compose up -d postgres redis
```

### 4. Inicie cada serviço

```bash
# Go — Diff Processor (porta 8081)
make dev-go

# Python — LangGraph Agent (porta 8000)
make dev-agent

# NestJS — API (porta 3000)
make dev-api

# Angular — Frontend (porta 4200)
make dev-app
```

Ou suba tudo de uma vez:

```bash
make dev
```

Acesse: [http://localhost:4200](http://localhost:4200)

---

## Estrutura do projeto

```
/
├── go/                     # Diff Processor
│   ├── cmd/
│   │   └── main.go
│   ├── internal/
│   │   ├── parser/         # Parser de unified diff
│   │   └── handler/        # HTTP handlers
│   └── Dockerfile
│
├── agent/                  # LangGraph Agent
│   ├── graph/
│   │   ├── state.py        # ReviewState (TypedDict)
│   │   ├── nodes.py        # security, performance, style, aggregator
│   │   └── graph.py        # StateGraph e edges
│   ├── schemas/
│   │   └── review.py       # Pydantic models (ReviewComment)
│   ├── main.py             # FastAPI app + SSE endpoint
│   └── Dockerfile
│
├── nest-api/               # NestJS API Gateway
│   ├── src/
│   │   ├── auth/           # JWT, Guards, Decorators
│   │   ├── review/         # Controller, Service, Entities
│   │   ├── diff/           # HTTP client para o serviço Go
│   │   └── agent/          # HTTP + SSE client para o agente
│   └── Dockerfile
│
├── angular-app/            # Angular Frontend
│   ├── src/app/
│   │   ├── auth/           # AuthService, AuthGuard
│   │   ├── review/         # ReviewService (SSE), componentes
│   │   │   ├── diff-input/
│   │   │   ├── diff-viewer/
│   │   │   ├── review-panel/
│   │   │   └── comment-card/
│   │   └── history/        # ReviewHistoryComponent
│   └── Dockerfile
│
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## API Reference

### `POST /reviews`

Submete um diff para revisão. Retorna SSE stream com os comentários.

**Body:**

```json
{
  "rawDiff": "diff --git a/main.go b/main.go\n..."
}
```

**SSE Events:**

```json
{ "category": "security",    "file": "main.go", "line": 42, "severity": "critical", "message": "...", "suggestion": "..." }
{ "category": "performance", "file": "main.go", "line": 17, "severity": "warning",  "message": "...", "suggestion": "..." }
{ "category": "style",       "file": "main.go", "line": 8,  "severity": "info",     "message": "...", "suggestion": "..." }
```

### `GET /reviews`

Lista reviews anteriores do usuário autenticado.

### `GET /reviews/:id`

Retorna os detalhes e comentários de um review específico.

---

## Severidades

| Nível      | Cor         | Descrição                         |
| ---------- | ----------- | --------------------------------- |
| `critical` | 🔴 Vermelho | Deve ser corrigido antes do merge |
| `warning`  | 🟡 Amarelo  | Recomendado corrigir              |
| `info`     | 🔵 Azul     | Sugestão ou observação            |

---

## Variáveis de ambiente

| Variável         | Serviço        | Descrição                                             |
| ---------------- | -------------- | ----------------------------------------------------- |
| `OPENAI_API_KEY` | Agent          | Chave da API do LLM                                   |
| `DATABASE_URL`   | NestJS         | Connection string do PostgreSQL                       |
| `REDIS_URL`      | NestJS / Agent | Connection string do Redis                            |
| `JWT_SECRET`     | NestJS         | Secret para assinar tokens JWT                        |
| `GO_SERVICE_URL` | NestJS         | URL do serviço Go (ex: `http://go-diff:8081`)         |
| `AGENT_URL`      | NestJS         | URL do agente Python (ex: `http://python-agent:8000`) |
| `API_URL`        | Angular        | URL da NestJS API (ex: `http://localhost:3000`)       |

---

## Testes

```bash
# Go
make test-go

# Python Agent
make test-agent

# NestJS (unitários + e2e)
make test-api

# Angular
make test-app

# Todos
make test
```

---

## Decisões de design

**Por que Go para o parser de diff?**
Diffs de PRs grandes podem ter centenas de arquivos e milhares de linhas. Go processa isso com baixa latência e sem overhead de runtime, liberando o NestJS para focar na orquestração.

**Por que LangGraph em vez de uma chain simples?**
O grafo de estados permite rodar os três reviewers em paralelo e tem suporte nativo a streaming por nó — cada reviewer emite comentários conforme termina, sem esperar os outros.

**Por que NestJS como gateway e não chamar o agente direto do Angular?**
O NestJS centraliza autenticação, persistência, rate limiting e a lógica de retry/circuit breaker. O Angular nunca fala diretamente com o agente Python.
