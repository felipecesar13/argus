# Code Review Assistant — Checklist de Implementação

---

## 01 — Setup & Estrutura

- [ ] Criar monorepo (nx ou turborepo) com workspaces: `/go`, `/agent`, `/nest-api`, `/angular-app`
- [ ] Configurar Docker Compose com serviços: `go-diff`, `python-agent`, `nest-api`, `angular`, `postgres`, `redis`
- [ ] Definir variáveis de ambiente (`.env.example`) para cada serviço
- [ ] Configurar rede interna Docker para comunicação entre serviços
- [ ] Criar `Makefile` com comandos: `dev`, `build`, `test`, `lint` para cada serviço

---

## 02 — Go: Diff Processor

- [x] Inicializar módulo Go: `go mod init diff-processor`
- [ ] Implementar parser de unified diff format (chunk por chunk)
- [ ] Detectar linguagem por extensão de arquivo (`.go`, `.ts`, `.py`, etc.)
- [ ] Criar struct `FileDiff` com campos: `Filename`, `Language`, `Additions`, `Deletions`, `Context`
- [ ] Implementar endpoint `POST /parse` que retorna `[]FileDiff`
- [ ] Adicionar validação de tamanho máximo do diff (ex: 500KB)
- [ ] Implementar health check endpoint `GET /health`
- [ ] Escrever testes unitários para o parser (casos: arquivo novo, deletado, renomeado, binário)
- [ ] Adicionar middleware de logging com `slog`
- [ ] Containerizar com Dockerfile multi-stage

---

## 03 — Python: LangGraph Agent

- [ ] Criar ambiente virtual e instalar: `langchain`, `langgraph`, `fastapi`, `uvicorn`
- [ ] Definir `ReviewState` com `TypedDict`: `diff_files`, `security_comments`, `performance_comments`, `style_comments`, `final_comments`
- [ ] Implementar nó `security_reviewer` com prompt focado em: SQL injection, secrets, auth, deps vulneráveis
- [ ] Implementar nó `performance_reviewer` com prompt focado em: complexidade, N+1, alocações desnecessárias
- [ ] Implementar nó `style_reviewer` com prompt focado em: nomenclatura, duplicação, responsabilidade única
- [ ] Implementar nó `aggregator` que consolida e deduplica comentários
- [ ] Montar o `StateGraph` com os 4 nós e edges corretos (3 reviewers em paralelo → aggregator)
- [ ] Configurar output parser com Pydantic: `ReviewComment(file, line, severity, category, message, suggestion)`
- [ ] Expor endpoint `POST /review` via FastAPI que retorna SSE stream
- [ ] Implementar retry com backoff para chamadas ao LLM
- [ ] Adicionar cache de resultados com Redis (hash do diff como chave)
- [ ] Escrever testes com diffs reais de exemplo para cada reviewer

---

## 04 — NestJS: API Gateway

- [x] Criar projeto NestJS com CLI: `nest new api`
- [ ] Configurar módulos: `AuthModule`, `ReviewModule`, `DiffModule`, `UserModule`
- [ ] Implementar autenticação JWT com Guards e Decorators
- [ ] Criar `DiffService` que faz HTTP para o serviço Go (`axios` ou `httpService`)
- [ ] Criar `AgentService` que consome o SSE do agente Python e repassa para o cliente
- [ ] Implementar `ReviewController` com: `POST /reviews`, `GET /reviews`, `GET /reviews/:id`
- [ ] Configurar SSE no controller com `@Sse()` decorator e `Observable`
- [ ] Criar entidades TypeORM: `Review`, `Comment`, `User`
- [ ] Implementar migrations do banco de dados
- [ ] Adicionar BullMQ para processar reviews assincronamente em fila
- [ ] Implementar rate limiting por usuário (throttler)
- [ ] Adicionar interceptor de logging e tratamento global de exceções
- [ ] Configurar Swagger com `@ApiTags`, `@ApiBody`, `@ApiResponse`
- [ ] Escrever testes e2e para os endpoints principais

---

## 05 — Angular: Frontend

- [x] Criar projeto Angular com: `ng new app --standalone --routing`
- [ ] Configurar `HttpClient`, `provideRouter` e interceptors no `app.config.ts`
- [ ] Criar `AuthService` com login, logout e armazenamento de JWT
- [ ] Criar `AuthGuard` para proteger rotas privadas
- [ ] Criar `ReviewService` com método `streamReview()` usando `EventSource` + `Observable`
- [ ] Criar componente `DiffInputComponent`: textarea para colar o diff + botão de submit
- [ ] Criar componente `DiffViewerComponent`: renderizar diff lado a lado com highlight de linhas
- [ ] Criar componente `ReviewPanelComponent`: abas por categoria (Security / Performance / Style)
- [ ] Criar componente `CommentCardComponent`: exibe severity, arquivo, linha, mensagem e sugestão
- [ ] Implementar animação de entrada dos comentários conforme chegam via SSE
- [ ] Criar `ReviewHistoryComponent` para listar reviews anteriores
- [ ] Implementar severity badge com cores: critical (vermelho), warning (amarelo), info (azul)
- [ ] Adicionar loading state e skeleton screens durante o streaming
- [ ] Escrever testes unitários para `ReviewService` e componentes principais

---

## 06 — Integração & Deploy

- [ ] Testar fluxo completo end-to-end com diff real de um PR público do GitHub
- [ ] Validar streaming SSE ponta a ponta (Go → Agent → NestJS → Angular)
- [ ] Configurar CORS no NestJS para o domínio do Angular
- [ ] Adicionar circuit breaker no NestJS para falha do agente Python
- [ ] Configurar GitHub Actions: lint + test em cada PR
- [ ] Escrever README com arquitetura, pré-requisitos e como rodar localmente
