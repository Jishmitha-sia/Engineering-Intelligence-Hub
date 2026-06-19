# Technical Design Document

> **Location**: `docs/specs/design.md`  
> **Last updated**: 19 June 2026

## Overview

The Engineering Intelligence Hub is a monolithic AI-powered SaaS platform that enables software teams to manage, search, and interact with technical documentation and GitHub repositories through advanced RAG (Retrieval-Augmented Generation) capabilities.

### Design Principles

1. **Simplicity Over Complexity**: Monolithic architecture optimized for solo developer maintenance
2. **Open Source Only**: No proprietary services or paid APIs in core functionality
3. **Production-Ready Patterns**: 80% production quality without enterprise overhead
4. **Portfolio Excellence**: Demonstrates AI Engineering capabilities for career advancement
5. **Developer Experience**: Easy local development and one-command deployment

### Key Design Decisions

- **Monolithic Architecture**: Single FastAPI backend, single Next.js frontend, avoiding microservices complexity
- **PostgreSQL + pgvector**: Unified database solution for relational data and vector search
- **Ollama for LLMs**: Local, free LLM inference for development and demonstration
- **Docker Compose**: Simple orchestration without Kubernetes overhead
- **Synchronous Core, Async Extensions**: FastAPI background tasks for document processing, avoiding message queue complexity

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│                     (Next.js Frontend)                          │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTPS / JWT Auth
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Auth Service │  │ RAG Pipeline │  │ GitHub Agent │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Doc Ingestion│  │ Eval System  │  │Self-Heal RAG│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼─────┐ ┌───▼──────────┐
│ PostgreSQL   │ │ Ollama │ │ File Storage │
│ + pgvector   │ │  LLM   │ │  (Volumes)   │
└──────────────┘ └────────┘ └──────────────┘
```

### Component Interactions

**User Authentication Flow**:
```
User → Frontend → POST /api/v1/auth/login → Auth Service → PostgreSQL
                                           ← JWT Token ←
```

**Document Ingestion Flow**:
```
User → Frontend → POST /api/v1/documents/upload → Document Service
                                                → Background Task
                                                → Text Extraction
                                                → Chunking (512 tokens, 50 overlap)
                                                → Embedding Model (BAAI/bge-small)
                                                → pgvector Storage
                                                → Status Update
```

**RAG Chat Flow**:
```
User Query → Frontend → POST /api/v1/chat → RAG Pipeline
                                          → Semantic Search (pgvector cosine similarity)
                                          → Reranker (BAAI/bge-reranker)
                                          → Context Assembly
                                          → Ollama LLM (qwen3:8b/llama3.1:8b)
                                          → Citation Generation
                                          → Response + Sources
```

**Self-Healing RAG Flow** (LangGraph):
```
User Query → Retriever Agent → Generator Agent → Critic Agent
                                                → Score Check (Faithfulness/Relevance)
                                                → If < 0.7: Query Rewriter Agent
                                                → Retry (max 2 iterations)
                                                → Final Answer
```

### Data Flow

1. **Ingestion Path**: Upload → Extract → Chunk → Embed → Store
2. **Retrieval Path**: Query → Embed → Search → Rerank → Context
3. **Generation Path**: Context + Query + History → LLM → Answer + Citations
4. **Evaluation Path**: Answer + Context → Metrics Calculation → Dashboard

### Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | Next.js 14 (App Router), TypeScript, TailwindCSS | Modern React framework, SSR/SSG, excellent DX |
| **Backend** | FastAPI (Python 3.11+), Pydantic V2 | Async support, automatic OpenAPI, type safety |
| **Database** | PostgreSQL 15 + pgvector | Unified relational + vector store, mature, reliable |
| **Embeddings** | BAAI/bge-small-en-v1.5 | Fast, small (133M params), good quality for English |
| **Reranker** | BAAI/bge-reranker-base | Improves retrieval precision without re-embedding |
| **LLM** | Ollama (qwen3:8b, llama3.1:8b) | Local inference, no API costs, privacy-friendly |
| **Agentic Framework** | LangGraph | State machine for self-healing RAG, observability |
| **Document Processing** | PyMuPDF, python-docx, markdownify | Fast PDF/DOCX/Markdown parsing |
| **Authentication** | JWT (python-jose), bcrypt | Industry standard, stateless, secure |
| **Testing** | Pytest, Playwright, Hypothesis | Unit, E2E, property-based testing |
| **Monitoring** | Loguru, Prometheus, Grafana | Structured logging, metrics, dashboards |
| **Deployment** | Docker Compose, GitHub Actions | Simple orchestration, CI/CD automation |

## Components and Interfaces

### Backend Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration management (pydantic-settings)
│   ├── dependencies.py              # Dependency injection (DB sessions, auth)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py            # API v1 router aggregation
│   │   │   ├── auth.py              # POST /login, /register, /logout
│   │   │   ├── workspaces.py        # CRUD /workspaces, /workspaces/{id}/members
│   │   │   ├── documents.py         # POST /documents/upload, GET /documents
│   │   │   ├── search.py            # POST /search (semantic search)
│   │   │   ├── chat.py              # POST /chat, GET /chat/history
│   │   │   ├── github.py            # POST /github/analyze
│   │   │   ├── evaluation.py        # GET /evaluation/metrics, /dashboard
│   │   │   └── analytics.py         # GET /analytics/*
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py              # JWT creation/validation, password hashing
│   │   ├── rate_limiter.py          # Rate limiting logic (slowapi)
│   │   └── exceptions.py            # Custom exception classes
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py               # SQLAlchemy engine, sessionmaker
│   │   ├── base.py                  # Base model, metadata
│   │   └── init_db.py               # Database initialization
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # User SQLAlchemy model
│   │   ├── workspace.py             # Workspace, WorkspaceMember models
│   │   ├── document.py              # Document, Chunk models
│   │   ├── chat.py                  # ChatSession, ChatMessage models
│   │   └── evaluation.py            # EvaluationMetric model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                  # Pydantic schemas for User
│   │   ├── workspace.py             # Pydantic schemas for Workspace
│   │   ├── document.py              # Pydantic schemas for Document
│   │   ├── chat.py                  # Pydantic schemas for Chat
│   │   └── evaluation.py            # Pydantic schemas for Metrics
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Authentication logic
│   │   ├── workspace_service.py     # Workspace management
│   │   ├── document_service.py      # Document upload, processing
│   │   ├── embedding_service.py     # Embedding generation (HuggingFace)
│   │   ├── vector_store.py          # pgvector operations
│   │   ├── rag_pipeline.py          # RAG orchestration
│   │   ├── github_service.py        # GitHub cloning, analysis
│   │   ├── self_healing_rag.py      # LangGraph self-healing RAG
│   │   └── evaluation_service.py    # Metrics calculation
│   │
│   ├── agents/                      # LangGraph agents for self-healing RAG
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Base agent class
│   │   ├── retriever_agent.py       # Context retrieval
│   │   ├── generator_agent.py       # Answer generation
│   │   ├── critic_agent.py          # Quality evaluation
│   │   └── query_rewriter_agent.py  # Query reformulation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── text_extraction.py       # PDF, DOCX, TXT, MD parsers
│   │   ├── chunking.py              # Text chunking (512 tokens, 50 overlap)
│   │   ├── logging.py               # Loguru configuration
│   │   └── metrics.py               # Prometheus metrics setup
│   │
│   └── alembic/                     # Database migrations
│       ├── versions/
│       └── env.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── conftest.py
│
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
└── pytest.ini
```

### Frontend Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx               # Root layout with providers
│   │   ├── page.tsx                 # Landing page
│   │   ├── globals.css              # Tailwind CSS
│   │   │
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx         # Login page
│   │   │   └── register/
│   │   │       └── page.tsx         # Registration page
│   │   │
│   │   └── (dashboard)/
│   │       ├── layout.tsx           # Dashboard layout with sidebar
│   │       ├── workspaces/
│   │       │   └── [id]/
│   │       │       ├── page.tsx     # Workspace overview
│   │       │       ├── documents/
│   │       │       │   └── page.tsx # Document management
│   │       │       ├── chat/
│   │       │       │   └── page.tsx # RAG chat interface
│   │       │       ├── search/
│   │       │       │   └── page.tsx # Semantic search
│   │       │       └── settings/
│   │       │           └── page.tsx # Workspace settings
│   │       │
│   │       ├── github/
│   │       │   └── page.tsx         # GitHub repo analysis
│   │       │
│   │       ├── evaluation/
│   │       │   └── page.tsx         # Evaluation dashboard
│   │       │
│   │       └── analytics/
│   │           └── page.tsx         # Analytics dashboard
│   │
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   └── ...
│   │   │
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   │
│   │   ├── workspace/
│   │   │   ├── WorkspaceList.tsx
│   │   │   ├── WorkspaceCard.tsx
│   │   │   └── MemberManager.tsx
│   │   │
│   │   ├── document/
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   └── DocumentCard.tsx
│   │   │
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── CitationCard.tsx
│   │   │
│   │   ├── search/
│   │   │   ├── SearchBar.tsx
│   │   │   └── SearchResults.tsx
│   │   │
│   │   ├── evaluation/
│   │   │   ├── MetricCard.tsx
│   │   │   └── MetricChart.tsx
│   │   │
│   │   └── common/
│   │       ├── Navbar.tsx
│   │       ├── Sidebar.tsx
│   │       └── LoadingSpinner.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                   # API client (axios)
│   │   ├── auth.ts                  # Auth utilities, JWT handling
│   │   └── utils.ts                 # General utilities
│   │
│   ├── hooks/
│   │   ├── useAuth.ts               # Authentication hook
│   │   ├── useWorkspace.ts          # Workspace state management
│   │   └── useChat.ts               # Chat state management
│   │
│   ├── contexts/
│   │   ├── AuthContext.tsx          # Auth context provider
│   │   └── WorkspaceContext.tsx     # Workspace context provider
│   │
│   └── types/
│       ├── api.ts                   # API response types
│       └── models.ts                # Domain model types
│
├── public/
│   └── ...
│
├── tests/
│   └── e2e/
│       └── ...
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── Dockerfile
└── playwright.config.ts
```

### Key Interfaces

#### Authentication Service Interface

```python
class AuthService:
    async def register_user(email: str, password: str) -> User
    async def authenticate_user(email: str, password: str) -> Optional[User]
    def create_access_token(user_id: int) -> str
    async def get_current_user(token: str) -> User
    def hash_password(password: str) -> str
    def verify_password(plain: str, hashed: str) -> bool
```

#### Document Service Interface

```python
class DocumentService:
    async def upload_document(file: UploadFile, workspace_id: int, user_id: int) -> Document
    async def process_document_background(document_id: int) -> None
    async def get_documents(workspace_id: int) -> List[Document]
    async def delete_document(document_id: int, user_id: int) -> None
```

#### Embedding Service Interface

```python
class EmbeddingService:
    def __init__(model_name: str = "BAAI/bge-small-en-v1.5")
    def generate_embedding(text: str) -> List[float]
    def batch_generate_embeddings(texts: List[str]) -> List[List[float]]
```

#### Vector Store Interface

```python
class VectorStore:
    async def store_chunks(chunks: List[Chunk], embeddings: List[List[float]]) -> None
    async def search(query_embedding: List[float], top_k: int, workspace_id: int) -> List[Chunk]
    async def rerank(chunks: List[Chunk], query: str) -> List[Chunk]
```

#### RAG Pipeline Interface

```python
class RAGPipeline:
    async def generate_answer(
        query: str, 
        workspace_id: int, 
        chat_history: List[ChatMessage]
    ) -> RAGResponse
    
    async def retrieve_context(query: str, workspace_id: int) -> List[Chunk]
    async def generate_from_context(query: str, context: List[Chunk]) -> str
    def generate_citations(context: List[Chunk]) -> List[Citation]
```

#### Self-Healing RAG Interface (LangGraph)

```python
class SelfHealingRAG:
    def __init__(
        retriever: RetrieverAgent,
        generator: GeneratorAgent,
        critic: CriticAgent,
        query_rewriter: QueryRewriterAgent
    )
    
    async def run(query: str, workspace_id: int, max_iterations: int = 2) -> RAGResponse
    
    # LangGraph state machine
    def build_graph() -> StateGraph

class RetrieverAgent:
    async def retrieve(state: AgentState) -> AgentState

class GeneratorAgent:
    async def generate(state: AgentState) -> AgentState

class CriticAgent:
    async def evaluate(state: AgentState) -> AgentState
    def calculate_faithfulness(answer: str, context: str) -> float
    def calculate_relevance(answer: str, query: str) -> float

class QueryRewriterAgent:
    async def rewrite(state: AgentState) -> AgentState
```

#### GitHub Service Interface

```python
class GitHubService:
    async def analyze_repository(repo_url: str, workspace_id: int, user_id: int) -> Document
    def clone_repository(repo_url: str, temp_dir: Path) -> None
    def extract_documentation(repo_path: Path) -> List[str]
    def generate_repository_overview(repo_path: Path) -> str
    def cleanup_temp_directory(temp_dir: Path) -> None
```

#### Evaluation Service Interface

```python
class EvaluationService:
    async def record_metrics(
        query: str,
        answer: str,
        context: List[Chunk],
        latency: float,
        tokens: int,
        workspace_id: int
    ) -> EvaluationMetric
    
    async def calculate_faithfulness(answer: str, context: str) -> float
    async def calculate_relevance(answer: str, query: str) -> float
    def calculate_context_precision(chunks: List[Chunk], query: str) -> float
    def calculate_context_recall(chunks: List[Chunk], query: str) -> float
    
    async def get_dashboard_metrics(workspace_id: int, days: int = 7) -> DashboardMetrics
```

## Data Models

### Database Schema

#### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**SQLAlchemy Model**:
```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    workspaces: Mapped[List["WorkspaceMember"]] = relationship(back_populates="user")
```

#### Workspaces Table

```sql
CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workspaces_created_by ON workspaces(created_by);
```

**SQLAlchemy Model**:
```python
class Workspace(Base):
    __tablename__ = "workspaces"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    members: Mapped[List["WorkspaceMember"]] = relationship(back_populates="workspace")
    documents: Mapped[List["Document"]] = relationship(back_populates="workspace")
```

#### Workspace Members Table

```sql
CREATE TABLE workspace_members (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'member')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
```

**SQLAlchemy Model**:
```python
class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(default=func.now())
    
    workspace: Mapped["Workspace"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="workspaces")
```

#### Documents Table

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    uploaded_by INTEGER REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'indexed', 'failed')),
    error_message TEXT,
    page_count INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE INDEX idx_documents_workspace ON documents(workspace_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);
```

**SQLAlchemy Model**:
```python
class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    uploaded_at: Mapped[datetime] = mapped_column(default=func.now())
    processed_at: Mapped[Optional[datetime]] = mapped_column()
    
    workspace: Mapped["Workspace"] = relationship(back_populates="documents")
    chunks: Mapped[List["Chunk"]] = relationship(back_populates="document")
```

#### Chunks Table (with pgvector)

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL,  -- BAAI/bge-small-en-v1.5 produces 384-dim vectors
    page_number INTEGER,
    chunk_index INTEGER NOT NULL,
    token_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunks_document ON chunks(document_id);
CREATE INDEX idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- Note: IVFFlat index created after significant data exists for better performance
```

**SQLAlchemy Model**:
```python
from pgvector.sqlalchemy import Vector

class Chunk(Base):
    __tablename__ = "chunks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(384), nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    
    document: Mapped["Document"] = relationship(back_populates="chunks")
```

#### Chat Sessions Table

```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_sessions_workspace ON chat_sessions(workspace_id);
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);
```

**SQLAlchemy Model**:
```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    messages: Mapped[List["ChatMessage"]] = relationship(back_populates="session")
```

#### Chat Messages Table

```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    citations JSONB,  -- Array of {document_id, page_number, chunk_id, relevance_score}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
```

**SQLAlchemy Model**:
```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    
    session: Mapped["ChatSession"] = relationship(back_populates="messages")
```

#### Evaluation Metrics Table

```sql
CREATE TABLE evaluation_metrics (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES chat_sessions(id) ON DELETE SET NULL,
    query TEXT NOT NULL,
    answer TEXT NOT NULL,
    faithfulness_score FLOAT,
    relevance_score FLOAT,
    context_precision FLOAT,
    context_recall FLOAT,
    response_latency_ms INTEGER NOT NULL,
    tokens_used INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evaluation_metrics_workspace ON evaluation_metrics(workspace_id);
CREATE INDEX idx_evaluation_metrics_created_at ON evaluation_metrics(created_at);
CREATE INDEX idx_evaluation_metrics_faithfulness ON evaluation_metrics(faithfulness_score);
```

**SQLAlchemy Model**:
```python
class EvaluationMetric(Base):
    __tablename__ = "evaluation_metrics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chat_sessions.id", ondelete="SET NULL"))
    query: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    faithfulness_score: Mapped[Optional[float]] = mapped_column(Float)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float)
    context_precision: Mapped[Optional[float]] = mapped_column(Float)
    context_recall: Mapped[Optional[float]] = mapped_column(Float)
    response_latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

### Database Indexes and Performance

**Index Strategy**:
1. **Primary Keys**: All tables have auto-incrementing integer primary keys
2. **Foreign Keys**: All foreign key columns are indexed for join performance
3. **Unique Constraints**: Email (users), workspace_id+user_id (workspace_members)
4. **Vector Search**: IVFFlat index on embeddings with cosine similarity
5. **Time-Series**: created_at indexed on time-sensitive queries (chat, metrics)
6. **Status Tracking**: status column indexed for filtering pending/processing documents

**pgvector Configuration**:
- **Embedding Dimension**: 384 (BAAI/bge-small-en-v1.5)
- **Distance Metric**: Cosine similarity (`vector_cosine_ops`)
- **Index Type**: IVFFlat with 100 lists (balance speed/accuracy for ~10M vectors)
- **Index Creation**: Defer until >10k chunks exist for optimal clustering

**Database Connection Pooling**:
```python
# SQLAlchemy async engine configuration
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Connection pool size
    max_overflow=10,        # Additional connections on demand
    pool_pre_ping=True,     # Check connection health before use
    echo=False              # Disable SQL logging in production
)
```

## API Architecture

### RESTful API Design

**Base URL**: `/api/v1`

**Versioning Strategy**: URL-based versioning for clear API evolution

**Standard Response Format**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Error Response Format**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "User-friendly error message",
    "details": { ... }
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### API Endpoints

#### Authentication Endpoints

```
POST /api/v1/auth/register
Request: { email, password, full_name }
Response: { user: { id, email, full_name }, token }

POST /api/v1/auth/login
Request: { email, password }
Response: { user: { id, email, full_name }, token }

POST /api/v1/auth/logout
Headers: Authorization: Bearer <token>
Response: { message: "Logged out successfully" }

GET /api/v1/auth/me
Headers: Authorization: Bearer <token>
Response: { user: { id, email, full_name } }
```

#### Workspace Endpoints

```
GET /api/v1/workspaces
Headers: Authorization: Bearer <token>
Response: { workspaces: [{ id, name, description, role, member_count }] }

POST /api/v1/workspaces
Headers: Authorization: Bearer <token>
Request: { name, description }
Response: { workspace: { id, name, description, created_at } }

GET /api/v1/workspaces/{workspace_id}
Headers: Authorization: Bearer <token>
Response: { workspace: { id, name, description, members: [...], document_count } }

PUT /api/v1/workspaces/{workspace_id}
Headers: Authorization: Bearer <token>
Request: { name, description }
Response: { workspace: { id, name, description, updated_at } }

DELETE /api/v1/workspaces/{workspace_id}
Headers: Authorization: Bearer <token>
Response: { message: "Workspace deleted" }

POST /api/v1/workspaces/{workspace_id}/members
Headers: Authorization: Bearer <token>
Request: { email, role }
Response: { member: { user_id, email, role, joined_at } }

DELETE /api/v1/workspaces/{workspace_id}/members/{user_id}
Headers: Authorization: Bearer <token>
Response: { message: "Member removed" }
```

#### Document Endpoints

```
POST /api/v1/documents/upload
Headers: Authorization: Bearer <token>, Content-Type: multipart/form-data
Request: FormData { file, workspace_id }
Response: { document: { id, filename, file_size, status, uploaded_at } }

GET /api/v1/documents
Headers: Authorization: Bearer <token>
Query: ?workspace_id={id}&status={status}&page={num}&limit={num}
Response: { documents: [...], total, page, pages }

GET /api/v1/documents/{document_id}
Headers: Authorization: Bearer <token>
Response: { document: { id, filename, file_size, status, page_count, chunks_count } }

DELETE /api/v1/documents/{document_id}
Headers: Authorization: Bearer <token>
Response: { message: "Document deleted" }

GET /api/v1/documents/{document_id}/chunks
Headers: Authorization: Bearer <token>
Query: ?page={num}&limit={num}
Response: { chunks: [{ id, content, page_number, chunk_index }], total, page, pages }
```

#### Search Endpoints

```
POST /api/v1/search
Headers: Authorization: Bearer <token>
Request: { query, workspace_id, top_k: 5 }
Response: { 
  results: [
    { 
      chunk_id, 
      document_id, 
      document_name, 
      content, 
      page_number, 
      relevance_score 
    }
  ],
  query_time_ms
}
```

#### Chat Endpoints

```
POST /api/v1/chat
Headers: Authorization: Bearer <token>
Request: { 
  query, 
  workspace_id, 
  session_id: optional,
  use_self_healing: false 
}
Response: { 
  answer, 
  citations: [{ document_id, document_name, page_number, chunk_id, score }],
  session_id,
  faithfulness_score: optional,
  relevance_score: optional,
  response_time_ms
}

GET /api/v1/chat/sessions
Headers: Authorization: Bearer <token>
Query: ?workspace_id={id}
Response: { sessions: [{ id, title, message_count, created_at, updated_at }] }

GET /api/v1/chat/sessions/{session_id}
Headers: Authorization: Bearer <token>
Response: { session: { id, title, messages: [{ role, content, citations, created_at }] } }

DELETE /api/v1/chat/sessions/{session_id}
Headers: Authorization: Bearer <token>
Response: { message: "Session deleted" }
```

#### GitHub Endpoints

```
POST /api/v1/github/analyze
Headers: Authorization: Bearer <token>
Request: { repo_url, workspace_id }
Response: { 
  job_id,
  status: "processing",
  message: "Repository analysis started"
}

GET /api/v1/github/analyze/{job_id}
Headers: Authorization: Bearer <token>
Response: { 
  job_id,
  status: "completed" | "processing" | "failed",
  document_id: optional,
  error: optional
}
```

#### Evaluation Endpoints

```
GET /api/v1/evaluation/dashboard
Headers: Authorization: Bearer <token>
Query: ?workspace_id={id}&days={7}
Response: {
  avg_faithfulness,
  avg_relevance,
  avg_context_precision,
  avg_context_recall,
  p95_latency_ms,
  total_tokens,
  total_queries,
  faithfulness_over_time: [{ date, score }],
  latency_over_time: [{ date, latency_ms }]
}

GET /api/v1/evaluation/metrics
Headers: Authorization: Bearer <token>
Query: ?workspace_id={id}&start_date={iso}&end_date={iso}&page={num}&limit={num}
Response: { 
  metrics: [{ 
    id, 
    query, 
    answer, 
    faithfulness_score, 
    relevance_score,
    context_precision,
    context_recall,
    response_latency_ms,
    tokens_used,
    created_at
  }],
  total,
  page,
  pages
}
```

#### Analytics Endpoints

```
GET /api/v1/analytics/overview
Headers: Authorization: Bearer <token>
Query: ?workspace_id={id}&days={7}
Response: {
  active_users_24h,
  total_queries_7d,
  total_documents_7d,
  total_tokens_7d,
  avg_response_time_7d
}

GET /api/v1/analytics/top-queries
Headers: Authorization: Bearer <token>
Query: ?workspace_id={id}&days={7}&limit={10}
Response: { queries: [{ query, count }] }

GET /api/v1/analytics/top-documents
Headers: Authorization: Bearer <token>
Query: ?workspace_id={id}&days={7}&limit={10}
Response: { documents: [{ document_id, filename, access_count }] }

GET /api/v1/analytics/export
Headers: Authorization: Bearer <token>
Query: ?workspace_id={id}&start_date={iso}&end_date={iso}&format=csv
Response: CSV file download
```

### Error Handling

**HTTP Status Codes**:
- `200 OK`: Successful GET/PUT/DELETE
- `201 Created`: Successful POST
- `400 Bad Request`: Validation errors
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource (e.g., email already exists)
- `413 Payload Too Large`: File size exceeds limit
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Unhandled server errors
- `503 Service Unavailable`: LLM or database unavailable

**Error Code System**:
```python
class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

**Global Exception Handler**:
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": getattr(exc, "error_code", "INTERNAL_ERROR"),
                "message": exc.detail,
                "details": getattr(exc, "details", None)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Authentication Architecture

### JWT Token Flow

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│  Client  │                │  Backend │                │   DB     │
└─────┬────┘                └─────┬────┘                └─────┬────┘
      │                           │                           │
      │ POST /auth/login          │                           │
      │ {email, password}         │                           │
      │──────────────────────────>│                           │
      │                           │ SELECT * FROM users       │
      │                           │ WHERE email = ?           │
      │                           │──────────────────────────>│
      │                           │                           │
      │                           │ <────────user row─────────│
      │                           │                           │
      │                           │ verify_password()         │
      │                           │ (bcrypt comparison)       │
      │                           │                           │
      │                           │ create_access_token()     │
      │                           │ (JWT with HS256)          │
      │                           │                           │
      │ {token, user}             │                           │
      │<──────────────────────────│                           │
      │                           │                           │
      │ Store token in localStorage                          │
      │                           │                           │
      │ GET /api/v1/documents     │                           │
      │ Authorization: Bearer {token}                        │
      │──────────────────────────>│                           │
      │                           │ decode_token()            │
      │                           │ validate_signature()      │
      │                           │ check_expiration()        │
      │                           │                           │
      │                           │ get_current_user()        │
      │                           │──────────────────────────>│
      │                           │                           │
      │                           │ <────────user row─────────│
      │                           │                           │
      │ {documents: [...]}        │                           │
      │<──────────────────────────│                           │
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "email": "user@example.com",
    "exp": 1705347600,
    "iat": 1705261200
  },
  "signature": "..."
}
```

### Password Security

**Hashing Strategy**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password, rounds=12)  # Cost factor 12

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Validated on frontend and backend

### Middleware Design

**Authentication Middleware**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
```

**Protected Route Example**:
```python
@router.get("/documents")
async def get_documents(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify workspace access
    await verify_workspace_access(workspace_id, current_user.id, db)
    documents = await document_service.get_documents(workspace_id, db)
    return {"documents": documents}
```

### Session Management

**Token Expiration**: 24 hours
**Refresh Strategy**: Client-side token refresh before expiration (not implemented in MVP)
**Logout**: Client-side token deletion (stateless JWT, no server-side session storage)

**Frontend Token Management**:
```typescript
// lib/auth.ts
export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  
  getToken: () => localStorage.getItem('token'),
  
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }
};
```

## Workspace Architecture

### Multi-Tenancy Model

**Workspace Isolation Strategy**:
- All data is scoped by `workspace_id`
- Database queries include `workspace_id` filter
- Workspace access verified on every request
- No cross-workspace data leakage

**Role-Based Access Control (RBAC)**:

| Role | Create Workspace | Invite Members | Remove Members | Upload Documents | Delete Documents | Delete Workspace | Chat |
|------|-----------------|----------------|----------------|------------------|------------------|------------------|------|
| **Owner** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Member** | ✓ | ✗ | ✗ | ✓ | Own only | ✗ | ✓ |

### Access Control Implementation

**Workspace Access Verification**:
```python
async def verify_workspace_access(
    workspace_id: int,
    user_id: int,
    db: AsyncSession,
    required_role: Optional[str] = None
) -> WorkspaceMember:
    stmt = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this workspace is forbidden"
        )
    
    if required_role == "owner" and member.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required for this action"
        )
    
    return member
```

**Dependency Injection for Access Control**:
```python
async def require_workspace_owner(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkspaceMember:
    return await verify_workspace_access(workspace_id, current_user.id, db, required_role="owner")

@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: int,
    member: WorkspaceMember = Depends(require_workspace_owner),
    db: AsyncSession = Depends(get_db)
):
    await workspace_service.delete_workspace(workspace_id, db)
    return {"message": "Workspace deleted"}
```

### Data Isolation Strategy

**Query Scoping**:
```python
# All queries automatically scoped by workspace
async def get_documents(workspace_id: int, db: AsyncSession) -> List[Document]:
    stmt = select(Document).where(Document.workspace_id == workspace_id)
    result = await db.execute(stmt)
    return result.scalars().all()

# Vector search also scoped
async def search_chunks(query_embedding: List[float], workspace_id: int, top_k: int) -> List[Chunk]:
    stmt = (
        select(Chunk)
        .join(Document)
        .where(Document.workspace_id == workspace_id)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

## Document Ingestion Architecture

### File Upload Flow

```
┌────────────────────────────────────────────────────────────────┐
│                         Upload Flow                            │
└────────────────────────────────────────────────────────────────┘
    
    User selects file → Frontend validates (size, type)
                     ↓
    POST /api/v1/documents/upload (multipart/form-data)
                     ↓
    Backend validates → Save to disk (/app/uploads/{workspace_id}/)
                     ↓
    Create Document record (status="pending")
                     ↓
    Return Document metadata to client
                     ↓
    Schedule background task (FastAPI BackgroundTasks)
                     ↓
    ┌────────────────────────────────────────────────────────────┐
    │             Background Processing Pipeline                 │
    └────────────────────────────────────────────────────────────┘
                     ↓
    Update status to "processing"
                     ↓
    Extract text (PyMuPDF for PDF, python-docx for DOCX)
                     ↓
    Chunk text (512 tokens, 50 overlap using tiktoken)
                     ↓
    Generate embeddings (batch processing with HuggingFace)
                     ↓
    Store chunks + embeddings in PostgreSQL
                     ↓
    Update status to "indexed", set processed_at
                     ↓
    Client polls GET /documents/{id} to check status
```

### Text Extraction

**PDF Extraction** (PyMuPDF):
```python
import fitz  # PyMuPDF

def extract_pdf_text(file_path: Path) -> List[PageText]:
    doc = fitz.open(file_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        pages.append(PageText(page_number=page_num, content=text))
    doc.close()
    return pages
```

**DOCX Extraction** (python-docx):
```python
from docx import Document

def extract_docx_text(file_path: Path) -> str:
    doc = Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n\n".join(paragraphs)
```

**TXT/Markdown Extraction**:
```python
def extract_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")
```

### Chunking Strategy

**Token-Based Chunking** (tiktoken):
```python
import tiktoken

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += (chunk_size - overlap)
    
    return chunks
```

**Chunking Parameters**:
- **Chunk Size**: 512 tokens (~2000 characters)
- **Overlap**: 50 tokens (~200 characters)
- **Rationale**: Balances context preservation with retrieval precision
- **Token Counting**: Uses tiktoken for accurate token measurement

**Chunk Metadata**:
```python
@dataclass
class ChunkMetadata:
    chunk_index: int       # Sequential index within document
    page_number: int       # Source page (PDF) or None (DOCX/TXT)
    token_count: int       # Actual token count
    char_count: int        # Character count
    start_char: int        # Character offset in original document
    end_char: int          # End character offset
```

### Embedding Generation

**Embedding Service** (HuggingFace):
```python
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # bge-small output dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def batch_generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        embeddings = self.model.encode(
            texts, 
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=True
        )
        return embeddings.tolist()
```

**Why BAAI/bge-small-en-v1.5**:
- Small model size (133M parameters)
- Fast inference (~50ms per embedding on CPU)
- High quality for English text
- 384-dimensional vectors (compact storage)
- Open source, no API costs

### Async Processing with Background Tasks

**FastAPI Background Tasks**:
```python
from fastapi import BackgroundTasks

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    workspace_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Save file to disk
    file_path = await save_upload_file(file, workspace_id)
    
    # Create document record
    document = await document_service.create_document(
        workspace_id=workspace_id,
        uploaded_by=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file.size,
        file_type=file.content_type,
        db=db
    )
    
    # Schedule background processing
    background_tasks.add_task(
        process_document_background,
        document.id,
        file_path
    )
    
    return {"document": document}

async def process_document_background(document_id: int, file_path: Path):
    async with get_async_session() as db:
        try:
            # Update status to processing
            await update_document_status(document_id, "processing", db)
            
            # Extract text
            text_pages = extract_text(file_path)
            
            # Chunk text
            chunks_data = []
            for page in text_pages:
                page_chunks = chunk_text(page.content)
                chunks_data.extend([
                    (chunk, page.page_number) 
                    for chunk in page_chunks
                ])
            
            # Generate embeddings (batch)
            texts = [chunk for chunk, _ in chunks_data]
            embeddings = embedding_service.batch_generate_embeddings(texts)
            
            # Store chunks
            await vector_store.store_chunks(document_id, chunks_data, embeddings, db)
            
            # Update status to indexed
            await update_document_status(document_id, "indexed", db)
            
        except Exception as e:
            logger.error(f"Document processing failed: {document_id}", exc_info=e)
            await update_document_status(document_id, "failed", db, error_message=str(e))
```

**No Message Queue Justification**:
- FastAPI BackgroundTasks sufficient for MVP
- Processing 100 pages/minute with single worker
- Failures logged and marked in database
- Avoids Redis, RabbitMQ, or Celery complexity
- Can upgrade to Celery if scale demands increase

## RAG Architecture

### RAG Pipeline Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      RAG Pipeline                              │
└────────────────────────────────────────────────────────────────┘

User Query
    ↓
┌───────────────────────┐
│ 1. Query Preprocessing│
│   - Load chat history │
│   - Prepare context   │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ 2. Semantic Search    │
│   - Generate query    │
│     embedding         │
│   - pgvector cosine   │
│     similarity        │
│   - Top 20 chunks     │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ 3. Reranking          │
│   - BAAI reranker     │
│   - Score chunks      │
│   - Top 5 chunks      │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ 4. Context Assembly   │
│   - Format chunks     │
│   - Add metadata      │
│   - Construct prompt  │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ 5. LLM Generation     │
│   - Ollama API call   │
│   - qwen3:8b or       │
│     llama3.1:8b       │
│   - Stream response   │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ 6. Citation Generation│
│   - Map chunks to     │
│     documents         │
│   - Add page numbers  │
│   - Calculate scores  │
└───────┬───────────────┘
        ↓
┌───────────────────────┐
│ 7. Store History      │
│   - Save query        │
│   - Save answer       │
│   - Save citations    │
└───────────────────────┘
        ↓
    Response
```

### Semantic Search Implementation

**Vector Search with pgvector**:
```python
async def semantic_search(
    query: str,
    workspace_id: int,
    top_k: int = 20,
    db: AsyncSession
) -> List[Chunk]:
    # Generate query embedding
    query_embedding = embedding_service.generate_embedding(query)
    
    # pgvector cosine similarity search
    stmt = (
        select(
            Chunk,
            Chunk.embedding.cosine_distance(query_embedding).label("distance")
        )
        .join(Document)
        .where(
            Document.workspace_id == workspace_id,
            Document.status == "indexed"
        )
        .order_by("distance")
        .limit(top_k)
    )
    
    result = await db.execute(stmt)
    chunks = [row.Chunk for row in result]
    return chunks
```

**Cosine Similarity**:
- Formula: `1 - cosine_distance(a, b)`
- Range: [0, 1], where 1 = identical, 0 = orthogonal
- pgvector optimized with IVFFlat index
- Fast approximate search for large datasets

### Reranking Pipeline

**Reranker Service** (BAAI/bge-reranker-base):
```python
from sentence_transformers import CrossEncoder

class RerankerService:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 5) -> List[Tuple[Chunk, float]]:
        # Prepare query-chunk pairs
        pairs = [(query, chunk.content) for chunk in chunks]
        
        # Score all pairs
        scores = self.model.predict(pairs)
        
        # Sort by score and take top_k
        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        return ranked
```

**Why Reranking**:
- Improves retrieval precision by 20-30%
- Cross-encoder (query+chunk) more accurate than bi-encoder (separate embeddings)
- Acceptable latency (~100ms for 20 chunks)
- Crucial for RAG answer quality

### Chat History Management

**History Retrieval**:
```python
async def get_chat_history(
    session_id: int,
    limit: int = 10,
    db: AsyncSession
) -> List[ChatMessage]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return list(reversed(messages))  # Chronological order
```

**Context Window Management**:
- Last 10 query-answer pairs included in prompt
- Approximately 4000 tokens of history
- Maintains conversational coherence
- Prevents context window overflow (8k token limit)

### Prompt Engineering

**System Prompt**:
```
You are an AI assistant helping software engineers understand technical documentation.

Your task is to answer questions based ONLY on the provided context.

Rules:
1. Only use information from the context provided
2. If the context doesn't contain the answer, say "I cannot find this information in the provided documents"
3. Include specific references to document sections when possible
4. Be concise but complete
5. If uncertain, acknowledge uncertainty rather than speculating

Context:
{context}

Chat History:
{chat_history}

User Question: {query}

Answer:
```

**Context Formatting**:
```python
def format_context(chunks: List[Tuple[Chunk, float]]) -> str:
    context_parts = []
    for i, (chunk, score) in enumerate(chunks, 1):
        context_parts.append(
            f"[Document: {chunk.document.filename}, Page: {chunk.page_number}, Relevance: {score:.2f}]\n"
            f"{chunk.content}\n"
        )
    return "\n---\n".join(context_parts)
```

### LLM Integration (Ollama)

**Ollama Client**:
```python
import httpx

class OllamaClient:
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.base_url = base_url
        self.model = "qwen3:8b"  # or llama3.1:8b
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.1
    ) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                        "top_p": 0.9
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"]
```

**LLM Configuration**:
- **Model**: qwen3:8b or llama3.1:8b (configurable)
- **Temperature**: 0.1 (low for factual answers)
- **Max Tokens**: 500 (concise answers)
- **Timeout**: 30 seconds
- **Streaming**: Disabled in MVP (can enable for better UX)

**Why Ollama**:
- Free, open-source LLM inference
- Docker-deployable, no external API
- Good 8B models (qwen3, llama3.1)
- Privacy-friendly (no data sent to external services)
- Sufficient quality for portfolio demonstration

### Citation Generation

**Citation Extraction**:
```python
@dataclass
class Citation:
    document_id: int
    document_name: str
    page_number: Optional[int]
    chunk_id: int
    relevance_score: float
    excerpt: str  # First 200 chars of chunk

def generate_citations(ranked_chunks: List[Tuple[Chunk, float]]) -> List[Citation]:
    citations = []
    for chunk, score in ranked_chunks:
        citations.append(Citation(
            document_id=chunk.document_id,
            document_name=chunk.document.filename,
            page_number=chunk.page_number,
            chunk_id=chunk.id,
            relevance_score=score,
            excerpt=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
        ))
    return citations
```

## GitHub Ingestion Architecture

### Repository Cloning Flow

```
User submits GitHub URL
         ↓
POST /api/v1/github/analyze
         ↓
Validate URL format
         ↓
Create job record (status="processing")
         ↓
Return job_id immediately
         ↓
Schedule background task
         ↓
┌──────────────────────────────────────┐
│   Background Repository Analysis     │
└──────────────────────────────────────┘
         ↓
Clone repo to /tmp/{job_id}/
         ↓
Extract documentation files:
  - README.md
  - CONTRIBUTING.md
  - docs/**/*.md
  - *.md (root level)
         ↓
Parse directory structure
         ↓
Generate repository overview document
         ↓
Create combined Document:
  - Title: "{repo_name} Documentation"
  - Content: All markdown files + overview
         ↓
Process through document ingestion pipeline
         ↓
Cleanup /tmp/{job_id}/
         ↓
Update job status to "completed"
```

### GitHub Service Implementation

```python
import subprocess
from pathlib import Path
from typing import List

class GitHubService:
    def __init__(self, temp_dir: Path = Path("/tmp/github_analysis")):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(exist_ok=True)
    
    async def analyze_repository(
        self,
        repo_url: str,
        workspace_id: int,
        user_id: int,
        db: AsyncSession
    ) -> str:
        job_id = str(uuid.uuid4())
        repo_path = self.temp_dir / job_id
        
        try:
            # Clone repository
            self.clone_repository(repo_url, repo_path)
            
            # Extract documentation
            docs = self.extract_documentation(repo_path)
            
            # Generate overview
            overview = self.generate_repository_overview(repo_path, docs)
            
            # Combine all content
            combined_content = self.combine_documentation(docs, overview)
            
            # Create document and process
            document = await self.create_github_document(
                workspace_id,
                user_id,
                repo_url,
                combined_content,
                db
            )
            
            return document.id
            
        finally:
            # Cleanup temp directory
            self.cleanup_temp_directory(repo_path)
    
    def clone_repository(self, repo_url: str, target_path: Path) -> None:
        subprocess.run(
            ["git", "clone", "--depth=1", repo_url, str(target_path)],
            check=True,
            capture_output=True
        )
```

    def extract_documentation(self, repo_path: Path) -> List[DocumentFile]:
        docs = []
        
        # Extract README
        for readme in ["README.md", "README.MD", "readme.md"]:
            readme_path = repo_path / readme
            if readme_path.exists():
                docs.append(DocumentFile(
                    path=str(readme_path),
                    content=readme_path.read_text(),
                    type="readme"
                ))
                break
        
        # Extract CONTRIBUTING
        contributing = repo_path / "CONTRIBUTING.md"
        if contributing.exists():
            docs.append(DocumentFile(
                path=str(contributing),
                content=contributing.read_text(),
                type="contributing"
            ))
        
        # Extract docs folder
        docs_dir = repo_path / "docs"
        if docs_dir.exists():
            for md_file in docs_dir.rglob("*.md"):
                docs.append(DocumentFile(
                    path=str(md_file.relative_to(repo_path)),
                    content=md_file.read_text(),
                    type="documentation"
                ))
        
        # Extract root-level markdown
        for md_file in repo_path.glob("*.md"):
            if md_file.name.upper() not in ["README.MD", "CONTRIBUTING.MD"]:
                docs.append(DocumentFile(
                    path=str(md_file.name),
                    content=md_file.read_text(),
                    type="markdown"
                ))
        
        return docs
    
    def generate_repository_overview(self, repo_path: Path, docs: List[DocumentFile]) -> str:
        # Analyze directory structure
        structure = self.analyze_directory_structure(repo_path)
        
        overview = f"""# Repository Overview

## Structure
{structure}

## Documentation Files
{chr(10).join(f"- {doc.path}" for doc in docs)}

## Key Components
{self.identify_key_components(repo_path)}
"""
        return overview
```

### Structure Analysis

**Directory Structure Parsing**:
```python
def analyze_directory_structure(self, repo_path: Path, max_depth: int = 3) -> str:
    lines = []
    
    def walk_directory(path: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return
        
        items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        for item in items:
            if item.name.startswith('.'):
                continue
            if item.name in ['node_modules', '__pycache__', 'venv', '.git']:
                continue
            
            lines.append(f"{prefix}{'📁' if item.is_dir() else '📄'} {item.name}")
            
            if item.is_dir():
                walk_directory(item, prefix + "  ", depth + 1)
    
    walk_directory(repo_path)
    return "\n".join(lines)

def identify_key_components(self, repo_path: Path) -> str:
    components = []
    
    # Detect backend
    if (repo_path / "requirements.txt").exists():
        components.append("- Python Backend (requirements.txt found)")
    if (repo_path / "package.json").exists():
        components.append("- Node.js Application (package.json found)")
    
    # Detect frontend frameworks
    package_json = repo_path / "package.json"
    if package_json.exists():
        content = package_json.read_text()
        if "react" in content.lower():
            components.append("- React Frontend")
        if "next" in content.lower():
            components.append("- Next.js Framework")
    
    # Detect database
    if (repo_path / "alembic").exists():
        components.append("- SQLAlchemy + Alembic (database migrations)")
    
    # Detect Docker
    if (repo_path / "Dockerfile").exists():
        components.append("- Docker containerization")
    if (repo_path / "docker-compose.yml").exists():
        components.append("- Docker Compose orchestration")
    
    return "\n".join(components) if components else "No key components detected"
```

## Self-Healing RAG Architecture

### LangGraph Agent Design

```
┌────────────────────────────────────────────────────────────────┐
│                   Self-Healing RAG State Machine               │
└────────────────────────────────────────────────────────────────┘

                    User Query
                        ↓
                ┌───────────────┐
                │ Initial State │
                │  - query      │
                │  - iteration=0│
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Retriever     │
                │ Agent         │
                │ - Semantic    │
                │   search      │
                │ - Get context │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Generator     │
                │ Agent         │
                │ - LLM call    │
                │ - Generate    │
                │   answer      │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Critic Agent  │
                │ - Faithfulness│
                │ - Relevance   │
                └───────┬───────┘
                        ↓
                 Quality Check
                /              \
               /                \
       Score >= 0.7         Score < 0.7
       OR iteration=2       AND iteration<2
              |                    |
              ↓                    ↓
        Final Answer       ┌───────────────┐
                          │ Query Rewriter│
                          │ Agent         │
                          │ - Reformulate │
                          │ - iteration++ │
                          └───────┬───────┘
                                  ↓
                          Back to Retriever
```

### Agent Implementation

**Agent State**:
```python
from typing import TypedDict, List

class AgentState(TypedDict):
    query: str
    original_query: str
    workspace_id: int
    iteration: int
    max_iterations: int
    context: List[Chunk]
    answer: str
    faithfulness_score: float
    relevance_score: float
    feedback: str
    final: bool
```

**Retriever Agent**:
```python
class RetrieverAgent:
    def __init__(self, vector_store: VectorStore, reranker: RerankerService):
        self.vector_store = vector_store
        self.reranker = reranker
    
    async def retrieve(self, state: AgentState) -> AgentState:
        # Semantic search
        chunks = await self.vector_store.search(
            query=state["query"],
            workspace_id=state["workspace_id"],
            top_k=20
        )
        
        # Rerank
        ranked_chunks = self.reranker.rerank(state["query"], chunks, top_k=5)
        
        state["context"] = [chunk for chunk, score in ranked_chunks]
        return state
```

**Generator Agent**:
```python
class GeneratorAgent:
    def __init__(self, llm_client: OllamaClient):
        self.llm_client = llm_client
    
    async def generate(self, state: AgentState) -> AgentState:
        # Format context
        context_str = self.format_context(state["context"])
        
        # Construct prompt
        prompt = f"""Context:
{context_str}

Question: {state["query"]}

Answer based ONLY on the context above:"""
        
        # Generate answer
        answer = await self.llm_client.generate(prompt, max_tokens=500)
        
        state["answer"] = answer
        return state
    
    def format_context(self, chunks: List[Chunk]) -> str:
        return "\n\n---\n\n".join([
            f"[Document: {chunk.document.filename}, Page: {chunk.page_number}]\n{chunk.content}"
            for chunk in chunks
        ])
```

**Critic Agent**:
```python
class CriticAgent:
    def __init__(self, llm_client: OllamaClient):
        self.llm_client = llm_client
    
    async def evaluate(self, state: AgentState) -> AgentState:
        # Calculate faithfulness
        faithfulness = await self.calculate_faithfulness(
            state["answer"],
            state["context"]
        )
        
        # Calculate relevance
        relevance = await self.calculate_relevance(
            state["answer"],
            state["query"]
        )
        
        state["faithfulness_score"] = faithfulness
        state["relevance_score"] = relevance
        
        # Generate feedback if scores are low
        if faithfulness < 0.7 or relevance < 0.7:
            state["feedback"] = self.generate_feedback(faithfulness, relevance)
        
        return state
    
    async def calculate_faithfulness(self, answer: str, context: List[Chunk]) -> float:
        context_str = " ".join([chunk.content for chunk in context])
        
        prompt = f"""Context: {context_str}

Answer: {answer}

Question: Does the answer contain information that is NOT present in the context?
Answer with a single number between 0 and 1, where 1 means fully faithful (all claims supported) and 0 means not faithful (contains unsupported claims).

Score:"""
        
        response = await self.llm_client.generate(prompt, max_tokens=10)
        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except ValueError:
            return 0.5  # Default if parsing fails
    
    async def calculate_relevance(self, answer: str, query: str) -> float:
        prompt = f"""Question: {query}

Answer: {answer}

Question: How relevant is the answer to the question?
Answer with a single number between 0 and 1, where 1 means fully relevant and 0 means not relevant.

Score:"""
        
        response = await self.llm_client.generate(prompt, max_tokens=10)
        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except ValueError:
            return 0.5
```

**Query Rewriter Agent**:
```python
class QueryRewriterAgent:
    def __init__(self, llm_client: OllamaClient):
        self.llm_client = llm_client
    
    async def rewrite(self, state: AgentState) -> AgentState:
        prompt = f"""Original Question: {state["original_query"]}

Current Query: {state["query"]}

Previous Answer Quality Issues:
{state["feedback"]}

Rewrite the query to be more specific and likely to retrieve better context. Focus on:
1. Adding technical terms if missing
2. Being more specific about what information is needed
3. Breaking down complex questions

Rewritten Query:"""
        
        rewritten = await self.llm_client.generate(prompt, max_tokens=100)
        
        state["query"] = rewritten.strip()
        state["iteration"] += 1
        
        return state
```

### LangGraph State Machine

```python
from langgraph.graph import StateGraph, END

class SelfHealingRAG:
    def __init__(
        self,
        retriever: RetrieverAgent,
        generator: GeneratorAgent,
        critic: CriticAgent,
        query_rewriter: QueryRewriterAgent
    ):
        self.retriever = retriever
        self.generator = generator
        self.critic = critic
        self.query_rewriter = query_rewriter
        self.graph = self.build_graph()
    
    def build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve", self.retriever.retrieve)
        workflow.add_node("generate", self.generator.generate)
        workflow.add_node("evaluate", self.critic.evaluate)
        workflow.add_node("rewrite", self.query_rewriter.rewrite)
        
        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "evaluate")
        
        # Conditional edge: retry or finish
        workflow.add_conditional_edges(
            "evaluate",
            self.should_continue,
            {
                "rewrite": "rewrite",
                "end": END
            }
        )
        workflow.add_edge("rewrite", "retrieve")
        
        return workflow.compile()
    
    def should_continue(self, state: AgentState) -> str:
        # Stop if quality is good or max iterations reached
        if state["faithfulness_score"] >= 0.7 and state["relevance_score"] >= 0.7:
            return "end"
        if state["iteration"] >= state["max_iterations"]:
            return "end"
        return "rewrite"
    
    async def run(self, query: str, workspace_id: int, max_iterations: int = 2) -> AgentState:
        initial_state: AgentState = {
            "query": query,
            "original_query": query,
            "workspace_id": workspace_id,
            "iteration": 0,
            "max_iterations": max_iterations,
            "context": [],
            "answer": "",
            "faithfulness_score": 0.0,
            "relevance_score": 0.0,
            "feedback": "",
            "final": False
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state
```

### Feedback Loop (Max 2 Iterations)

**Iteration Strategy**:
- **Iteration 0**: Initial query → retrieve → generate → evaluate
- **Iteration 1**: If quality < 0.7, rewrite query → retrieve → generate → evaluate
- **Iteration 2**: If still < 0.7, rewrite again → retrieve → generate → evaluate
- **Stop Condition**: Quality >= 0.7 OR iterations >= 2

**Why Limit to 2 Iterations**:
- Prevents infinite loops
- Balances quality improvement vs. latency
- Empirically, 2 iterations provide 80% of potential improvement
- Total latency: ~8-12 seconds for 2 iterations (acceptable for MVP)

### State Management

**State Persistence**:
- Agent state stored in-memory during execution
- Final state logged to database (evaluation_metrics table)
- Intermediate states discarded (no persistent storage overhead)

**State Transitions Logging**:
```python
import structlog

logger = structlog.get_logger()

async def log_state_transition(state: AgentState, node: str):
    logger.info(
        "self_healing_rag_transition",
        node=node,
        iteration=state["iteration"],
        faithfulness=state.get("faithfulness_score"),
        relevance=state.get("relevance_score"),
        query=state["query"][:100]
    )
```

## Evaluation Architecture

### Metrics Calculation

**Faithfulness** (LLM-based):
```python
async def calculate_faithfulness(answer: str, context: str, llm: OllamaClient) -> float:
    """
    Measures whether answer claims are supported by context.
    Uses LLM to evaluate claim grounding.
    """
    prompt = f"""Context: {context}

Answer: {answer}

Task: Evaluate if all factual claims in the answer are supported by the context.
Return a score from 0 to 1:
- 1.0 = All claims fully supported
- 0.5 = Some claims supported
- 0.0 = No claims supported

Score:"""
    
    response = await llm.generate(prompt, max_tokens=10, temperature=0.0)
    try:
        return float(response.strip())
    except ValueError:
        return 0.5
```

**Relevance** (LLM-based):
```python
async def calculate_relevance(answer: str, query: str, llm: OllamaClient) -> float:
    """
    Measures whether answer addresses the query.
    Uses LLM to evaluate answer-query alignment.
    """
    prompt = f"""Question: {query}

Answer: {answer}

Task: Evaluate if the answer directly addresses the question.
Return a score from 0 to 1:
- 1.0 = Perfectly addresses question
- 0.5 = Partially addresses question
- 0.0 = Does not address question

Score:"""
    
    response = await llm.generate(prompt, max_tokens=10, temperature=0.0)
    try:
        return float(response.strip())
    except ValueError:
        return 0.5
```

**Context Precision**:
```python
def calculate_context_precision(chunks: List[Chunk], query: str, reranker: RerankerService) -> float:
    """
    Measures ratio of relevant chunks in retrieved context.
    Uses reranker scores as relevance proxy.
    """
    scores = reranker.score_batch(query, [chunk.content for chunk in chunks])
    relevant_count = sum(1 for score in scores if score > 0.5)
    return relevant_count / len(chunks) if chunks else 0.0
```

**Context Recall**:
```python
def calculate_context_recall(chunks: List[Chunk], answer: str) -> float:
    """
    Measures coverage of context in final answer.
    Simple heuristic: ratio of chunks referenced in answer.
    """
    referenced_count = sum(
        1 for chunk in chunks 
        if any(sentence in answer for sentence in chunk.content.split('. ')[:3])
    )
    return referenced_count / len(chunks) if chunks else 0.0
```

### Async Metric Computation

**Background Metric Calculation**:
```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    start_time = time.time()
    
    # Generate answer (synchronous part)
    result = await rag_pipeline.generate_answer(
        query=request.query,
        workspace_id=request.workspace_id,
        session_id=request.session_id,
        db=db
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Schedule async metric calculation
    background_tasks.add_task(
        record_evaluation_metrics,
        query=request.query,
        answer=result.answer,
        context=result.context,
        latency_ms=latency_ms,
        tokens=result.tokens_used,
        workspace_id=request.workspace_id
    )
    
    return result

async def record_evaluation_metrics(
    query: str,
    answer: str,
    context: List[Chunk],
    latency_ms: int,
    tokens: int,
    workspace_id: int
):
    async with get_async_session() as db:
        # Calculate metrics
        faithfulness = await calculate_faithfulness(answer, context)
        relevance = await calculate_relevance(answer, query)
        precision = calculate_context_precision(context, query)
        recall = calculate_context_recall(context, answer)
        
        # Store in database
        metric = EvaluationMetric(
            workspace_id=workspace_id,
            query=query,
            answer=answer,
            faithfulness_score=faithfulness,
            relevance_score=relevance,
            context_precision=precision,
            context_recall=recall,
            response_latency_ms=latency_ms,
            tokens_used=tokens
        )
        db.add(metric)
        await db.commit()
```

**Why Async**:
- Don't block chat response waiting for metrics
- Metrics take 2-3 seconds (additional LLM calls)
- User gets answer immediately, metrics calculated in background
- Acceptable delay for dashboard updates

### Dashboard Data Aggregation

**Dashboard Query**:
```python
async def get_dashboard_metrics(workspace_id: int, days: int = 7) -> DashboardMetrics:
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    stmt = select(
        func.avg(EvaluationMetric.faithfulness_score).label("avg_faithfulness"),
        func.avg(EvaluationMetric.relevance_score).label("avg_relevance"),
        func.avg(EvaluationMetric.context_precision).label("avg_precision"),
        func.avg(EvaluationMetric.context_recall).label("avg_recall"),
        func.percentile_cont(0.95).within_group(
            EvaluationMetric.response_latency_ms
        ).label("p95_latency"),
        func.sum(EvaluationMetric.tokens_used).label("total_tokens"),
        func.count(EvaluationMetric.id).label("total_queries")
    ).where(
        EvaluationMetric.workspace_id == workspace_id,
        EvaluationMetric.created_at >= start_date
    )
    
    result = await db.execute(stmt)
    row = result.one()
    
    return DashboardMetrics(
        avg_faithfulness=row.avg_faithfulness or 0.0,
        avg_relevance=row.avg_relevance or 0.0,
        avg_context_precision=row.avg_precision or 0.0,
        avg_context_recall=row.avg_recall or 0.0,
        p95_latency_ms=row.p95_latency or 0,
        total_tokens=row.total_tokens or 0,
        total_queries=row.total_queries or 0
    )
```

**Time-Series Data**:
```python
async def get_faithfulness_over_time(workspace_id: int, days: int = 7) -> List[TimeSeriesPoint]:
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    stmt = select(
        func.date_trunc('hour', EvaluationMetric.created_at).label("time_bucket"),
        func.avg(EvaluationMetric.faithfulness_score).label("score")
    ).where(
        EvaluationMetric.workspace_id == workspace_id,
        EvaluationMetric.created_at >= start_date
    ).group_by("time_bucket").order_by("time_bucket")
    
    result = await db.execute(stmt)
    return [
        TimeSeriesPoint(timestamp=row.time_bucket, value=row.score)
        for row in result
    ]
```

## Deployment Architecture

### Docker Compose Services

```yaml
version: '3.8'

services:
  # PostgreSQL with pgvector
  postgres:
    image: ankane/pgvector:latest
    environment:
      POSTGRES_DB: engineering_hub
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Ollama LLM service
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]  # Optional: GPU acceleration

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/engineering_hub
      OLLAMA_BASE_URL: http://ollama:11434
      SECRET_KEY: ${SECRET_KEY}
      EMBEDDING_MODEL: BAAI/bge-small-en-v1.5
      RERANKER_MODEL: BAAI/bge-reranker-base
      LLM_MODEL: qwen3:8b
    volumes:
      - document_uploads:/app/uploads
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      ollama:
        condition: service_started
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
    command: npm run dev

  # Prometheus (optional for monitoring)
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  # Grafana (optional for visualization)
  grafana:
    image: grafana/grafana:latest
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

volumes:
  postgres_data:
  ollama_models:
  document_uploads:
  prometheus_data:
  grafana_data:
```

### Container Orchestration

**Service Dependencies**:
```
postgres (healthcheck) → backend → frontend
ollama → backend
prometheus → grafana
```

**Startup Order**:
1. PostgreSQL starts and passes healthcheck
2. Ollama starts (no healthcheck, starts immediately)
3. Backend waits for PostgreSQL healthcheck
4. Frontend starts after backend
5. Prometheus and Grafana start independently

### Volume Management

**Persistent Volumes**:
- `postgres_data`: Database persistence
- `ollama_models`: Downloaded LLM models (qwen3:8b ~4.5GB, llama3.1:8b ~4.7GB)
- `document_uploads`: User-uploaded documents
- `prometheus_data`: Metrics history
- `grafana_data`: Dashboard configurations

**Backup Strategy**:
```bash
# Backup database
docker exec postgres pg_dump -U postgres engineering_hub > backup.sql

# Backup uploads
docker run --rm -v document_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads.tar.gz -C /data .

# Restore database
docker exec -i postgres psql -U postgres engineering_hub < backup.sql

# Restore uploads
docker run --rm -v document_uploads:/data -v $(pwd):/backup alpine tar xzf /backup/uploads.tar.gz -C /data
```

### Network Configuration

**Internal Network**:
- All services communicate via Docker internal network
- Service discovery via service names (e.g., `postgres`, `ollama`)
- No external access except exposed ports

**Port Mapping**:
- `3000`: Frontend (Next.js)
- `8000`: Backend API (FastAPI)
- `5432`: PostgreSQL (development only)
- `11434`: Ollama (development only)
- `9090`: Prometheus (optional)
- `3001`: Grafana (optional)

### Environment Variable Strategy

**.env.example**:
```bash
# Database
POSTGRES_PASSWORD=changeme

# Security
SECRET_KEY=your-secret-key-minimum-32-characters

# LLM Configuration
OLLAMA_BASE_URL=http://ollama:11434
LLM_MODEL=qwen3:8b
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
RERANKER_MODEL=BAAI/bge-reranker-base

# Monitoring (optional)
GRAFANA_PASSWORD=admin

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**.env (gitignored)**:
- Copy from .env.example
- Fill in actual secrets
- Never commit to git

**Configuration Loading** (pydantic-settings):
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24
    
    # LLM
    ollama_base_url: str
    llm_model: str = "qwen3:8b"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "BAAI/bge-reranker-base"
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Docker Architecture

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

**Multi-Stage Build (Production)**:
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Development command (overridden in docker-compose)
CMD ["npm", "run", "dev"]
```

**Multi-Stage Build (Production)**:
```dockerfile
# Dependencies stage
FROM node:18-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

# Runtime stage
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Image Optimization

**Layer Caching Strategy**:
1. Copy dependency files first (package.json, requirements.txt)
2. Install dependencies (cached if files unchanged)
3. Copy application code last (invalidates cache only for code changes)

**Size Optimization**:
- Use slim/alpine base images
- Multi-stage builds for production
- Remove build dependencies in final stage
- Use `.dockerignore` to exclude unnecessary files

**.dockerignore** (Backend):
```
__pycache__
*.pyc
*.pyo
*.pyd
.env
.venv
venv/
.git
.pytest_cache
.coverage
htmlcov/
uploads/
*.log
```

**.dockerignore** (Frontend):
```
node_modules
.next
.git
.env.local
.env.*.local
*.log
npm-debug.log*
coverage/
```

## CI/CD Architecture

### GitHub Actions Workflow

**.github/workflows/ci-cd.yml**:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: ankane/pgvector:latest
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run linting
        working-directory: ./backend
        run: |
          black --check .
          flake8 .
          mypy .
      
      - name: Run tests
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
        run: |
          pytest --cov=app --cov-report=xml --cov-report=html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run linting
        working-directory: ./frontend
        run: npm run lint
      
      - name: Run tests
        working-directory: ./frontend
        run: npm run test:ci
      
      - name: Build
        working-directory: ./frontend
        run: npm run build

  deploy:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up
```

### Testing Pipeline

**Backend Testing** (Pytest):
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v

# Coverage report
pytest --cov=app --cov-report=html --cov-report=term
```

**Frontend Testing** (Jest + Playwright):
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

### Build and Deployment Automation

**Railway Deployment**:
```yaml
# railway.json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Render Deployment** (render.yaml):
```yaml
services:
  - type: web
    name: engineering-hub-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: engineering-hub-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: OLLAMA_BASE_URL
        value: http://ollama:11434

  - type: web
    name: engineering-hub-frontend
    env: node
    buildCommand: npm ci && npm run build
    startCommand: npm start
    envVars:
      - key: NEXT_PUBLIC_API_URL
        value: https://engineering-hub-backend.onrender.com

databases:
  - name: engineering-hub-db
    databaseName: engineering_hub
    user: postgres
    plan: starter
```

### Environment Promotion

**Development → Staging → Production**:
1. **Development**: Local Docker Compose
2. **Staging**: Railway/Render preview deployments
3. **Production**: Railway/Render production service

**Branch Strategy**:
- `develop`: Development environment
- `main`: Production environment
- Feature branches: PR preview deployments

## Error Handling

### Error Categories

1. **Validation Errors** (400): Invalid input, malformed requests
2. **Authentication Errors** (401): Invalid/expired tokens
3. **Authorization Errors** (403): Insufficient permissions
4. **Not Found Errors** (404): Resource doesn't exist
5. **Conflict Errors** (409): Duplicate resources
6. **Rate Limit Errors** (429): Too many requests
7. **Processing Errors** (500): Document processing failures
8. **External Service Errors** (503): LLM/database unavailable

### Error Handling Strategy

**Validation Errors**:
```python
from pydantic import ValidationError

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        }
    )
```

**Database Errors**:
```python
from sqlalchemy.exc import IntegrityError

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    if "duplicate key" in str(exc):
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error": {
                    "code": "DUPLICATE_RESOURCE",
                    "message": "Resource already exists"
                }
            }
        )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database operation failed"
            }
        }
    )
```

**External Service Errors**:
```python
import httpx

async def call_ollama_with_retry(prompt: str, max_retries: int = 2):
    for attempt in range(max_retries):
        try:
            response = await ollama_client.generate(prompt)
            return response
        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=503,
                    detail="LLM service unavailable"
                )
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Logging Strategy

**Loguru Configuration**:
```python
from loguru import logger
import sys

# Configure loguru
logger.remove()  # Remove default handler

# Console logging (development)
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="INFO"
)

# File logging (production)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="100 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="INFO"
)

# Error file logging
logger.add(
    "logs/errors_{time:YYYY-MM-DD}.log",
    rotation="50 MB",
    retention="14 days",
    level="ERROR"
)
```

**Request ID Middleware**:
```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    
    logger.bind(request_id=request_id).info(
        f"{request.method} {request.url.path}"
    )
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

**Structured Logging**:
```python
logger.info("document_upload_started", 
    document_id=document.id,
    workspace_id=workspace_id,
    file_size=file.size,
    user_id=current_user.id
)

logger.error("document_processing_failed",
    document_id=document.id,
    error=str(e),
    exc_info=True
)
```

## Testing Strategy

### Testing Pyramid

```
           ┌─────────────┐
           │     E2E     │  10% (Critical user flows)
           └─────────────┘
         ┌─────────────────┐
         │  Integration    │  20% (API endpoints, DB)
         └─────────────────┘
       ┌─────────────────────┐
       │      Unit Tests     │  70% (Functions, classes)
       └─────────────────────┘
```

### Unit Testing

**Backend Unit Tests** (Pytest):
```python
# tests/unit/services/test_embedding_service.py
import pytest
from app.services.embedding_service import EmbeddingService

@pytest.fixture
def embedding_service():
    return EmbeddingService(model_name="BAAI/bge-small-en-v1.5")

def test_generate_embedding_returns_correct_dimension(embedding_service):
    text = "This is a test sentence"
    embedding = embedding_service.generate_embedding(text)
    assert len(embedding) == 384

def test_batch_generate_embeddings(embedding_service):
    texts = ["First sentence", "Second sentence", "Third sentence"]
    embeddings = embedding_service.batch_generate_embeddings(texts)
    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)
```

**Frontend Unit Tests** (Jest + React Testing Library):
```typescript
// components/chat/__tests__/ChatInterface.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from '../ChatInterface';

describe('ChatInterface', () => {
  it('sends message on submit', async () => {
    const mockOnSend = jest.fn();
    render(<ChatInterface onSend={mockOnSend} />);
    
    const input = screen.getByPlaceholderText('Ask a question...');
    const submitButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(input, { target: { value: 'Test query' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnSend).toHaveBeenCalledWith('Test query');
    });
  });
});
```

### Integration Testing

**API Integration Tests**:
```python
# tests/integration/test_auth_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_login_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "full_name": "Test User"
            }
        )
        assert register_response.status_code == 201
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!"
            }
        )
        assert login_response.status_code == 200
        data = login_response.json()
        assert "token" in data
        
        # Access protected route
        token = data["token"]
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
```

**RAG Pipeline Integration Tests**:
```python
# tests/integration/test_rag_pipeline.py
@pytest.mark.asyncio
async def test_rag_pipeline_end_to_end(db_session, sample_document):
    # Setup: Document with chunks in database
    workspace_id = 1
    query = "What is the main topic?"
    
    # Execute RAG pipeline
    result = await rag_pipeline.generate_answer(
        query=query,
        workspace_id=workspace_id,
        chat_history=[],
        db=db_session
    )
    
    # Assertions
    assert result.answer is not None
    assert len(result.answer) > 0
    assert len(result.citations) > 0
    assert all(c.relevance_score > 0 for c in result.citations)
```

### End-to-End Testing

**Playwright E2E Tests**:
```typescript
// tests/e2e/auth-flow.spec.ts
import { test, expect } from '@playwright/test';

test('complete authentication flow', async ({ page }) => {
  // Navigate to register page
  await page.goto('http://localhost:3000/register');
  
  // Fill registration form
  await page.fill('input[name="email"]', 'e2e@example.com');
  await page.fill('input[name="password"]', 'SecurePass123!');
  await page.fill('input[name="fullName"]', 'E2E Test User');
  await page.click('button[type="submit"]');
  
  // Should redirect to dashboard
  await expect(page).toHaveURL(/\/workspaces/);
  
  // Logout
  await page.click('button[aria-label="User menu"]');
  await page.click('text=Logout');
  
  // Should redirect to login
  await expect(page).toHaveURL('/login');
  
  // Login with same credentials
  await page.fill('input[name="email"]', 'e2e@example.com');
  await page.fill('input[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');
  
  // Should be back at dashboard
  await expect(page).toHaveURL(/\/workspaces/);
});

test('upload and chat with document', async ({ page, context }) => {
  // Login first
  await page.goto('http://localhost:3000/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');
  
  // Navigate to documents
  await page.click('text=Documents');
  
  // Upload document
  const fileInput = await page.locator('input[type="file"]');
  await fileInput.setInputFiles('test-data/sample.pdf');
  
  // Wait for upload to complete
  await expect(page.locator('text=Processing')).toBeVisible();
  await expect(page.locator('text=Indexed')).toBeVisible({ timeout: 60000 });
  
  // Navigate to chat
  await page.click('text=Chat');
  
  // Send query
  await page.fill('textarea[placeholder*="Ask"]', 'What is the main topic?');
  await page.click('button[aria-label="Send"]');
  
  // Wait for response
  await expect(page.locator('.message.assistant')).toBeVisible({ timeout: 10000 });
  
  // Check for citations
  await expect(page.locator('.citation')).toBeVisible();
});
```

### Property-Based Testing

**Hypothesis for Backend**:
```python
# tests/property/test_chunking.py
from hypothesis import given, strategies as st
from app.utils.chunking import chunk_text

@given(
    text=st.text(min_size=100, max_size=10000),
    chunk_size=st.integers(min_value=100, max_value=1000),
    overlap=st.integers(min_value=0, max_value=100)
)
def test_chunk_text_properties(text, chunk_size, overlap):
    """Property: Chunking should preserve all text content"""
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    
    # Property 1: At least one chunk
    assert len(chunks) > 0
    
    # Property 2: Each chunk is within size limits (with tolerance for token encoding)
    for chunk in chunks:
        assert len(chunk) <= chunk_size * 6  # ~6 chars per token on average
    
    # Property 3: Chunks cover the original text
    # (approximate due to overlap and tokenization)
    combined_length = sum(len(chunk) for chunk in chunks)
    assert combined_length >= len(text) * 0.8  # Allow 20% margin

@given(query=st.text(min_size=10, max_size=500))
def test_embedding_determinism(query):
    """Property: Same query produces same embedding"""
    embedding1 = embedding_service.generate_embedding(query)
    embedding2 = embedding_service.generate_embedding(query)
    
    assert embedding1 == embedding2
```

### Test Coverage Goals

**Backend Coverage Targets**:
- Overall: 70%+
- Services layer: 80%+
- API endpoints: 75%+
- Utils: 85%+

**Frontend Coverage Targets**:
- Overall: 60%+
- Components: 65%+
- Hooks: 70%+
- Utils: 80%+

**Coverage Enforcement**:
```yaml
# .github/workflows/ci.yml
- name: Check coverage
  run: |
    pytest --cov=app --cov-fail-under=70
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

The following correctness properties are suitable for property-based testing. They represent universal behaviors that should hold across all valid inputs, focusing on core logic rather than infrastructure or external service integration.

### Property 1: Password Hashing Security

*For any* valid password, the system SHALL hash it using bcrypt with cost factor ≥ 12, and the hash SHALL be verifiable against the original password.

**Validates: Requirements 1.1, 1.6**

### Property 2: JWT Token Round-Trip

*For any* valid user credentials, generating a JWT token and then decoding it SHALL preserve the user ID and email, and the token SHALL have correct 24-hour expiration.

**Validates: Requirements 1.2, 1.7**

### Property 3: Token Expiration Enforcement

*For any* expired JWT token, attempting to access a protected route SHALL result in 401 Unauthorized response.

**Validates: Requirements 1.5, 1.7**

### Property 4: Workspace Owner Assignment

*For any* user creating a workspace, the system SHALL assign that user as Owner role in the workspace_members table.

**Validates: Requirements 2.1**

### Property 5: Authorization Enforcement

*For any* member (non-owner) attempting to delete a workspace, the system SHALL return 403 Forbidden.

**Validates: Requirements 2.4**

### Property 6: Text Chunking Preservation

*For any* text content, chunking with 512-token size and 50-token overlap SHALL preserve all content such that concatenating chunks reconstructs at least 80% of the original text (accounting for tokenization).

**Validates: Requirements 3.4**

### Property 7: Embedding Determinism

*For any* text input, generating embeddings multiple times SHALL produce identical 384-dimensional vectors.

**Validates: Requirements 3.5**

### Property 8: Chunk-Document Association

*For any* processed document, all generated chunks SHALL correctly reference their source document ID and page number.

**Validates: Requirements 3.7**

### Property 9: Document Status Transitions

*For any* document upload, the status SHALL transition from "pending" → "processing" → "indexed" (on success) or "failed" (on error), never skipping states or reverting.

**Validates: Requirements 3.8, 3.9**

### Property 10: Semantic Search Result Limit

*For any* search query with top_k parameter, the system SHALL return at most top_k results, never more.

**Validates: Requirements 4.2, 4.4**

### Property 11: Citation Completeness

*For any* search result or RAG answer, all citations SHALL include document name, page number (or null), and relevance score ≥ 0.

**Validates: Requirements 4.5, 5.4**

### Property 12: Chat History Limit

*For any* chat session, retrieving history for prompt context SHALL return at most the last 10 query-answer pairs, ordered chronologically.

**Validates: Requirements 5.6**

### Property 13: Answer Token Limit

*For any* RAG-generated answer, the token count SHALL not exceed 500 tokens.

**Validates: Requirements 5.9**

### Property 14: Temporary File Cleanup

*For any* GitHub repository analysis, temporary cloned files SHALL be deleted after processing completes or on error.

**Validates: Requirements 6.6**

### Property 15: Self-Healing Iteration Limit

*For any* query in the self-healing RAG system, the system SHALL perform at most 2 retry iterations regardless of quality scores.

**Validates: Requirements 8.7**

### Property 16: Critic Score Bounds

*For any* answer-context pair evaluated by the Critic Agent, faithfulness and relevance scores SHALL be in the range [0.0, 1.0].

**Validates: Requirements 8.3**

### Property 17: Rate Limit Enforcement

*For any* sequence of API requests from a single user exceeding 100 requests per minute, the system SHALL return 429 status code and SHALL reset the counter at the start of the next minute window.

**Validates: Requirements 14.1, 14.2, 14.6**

### Property 18: Error Logging Consistency

*For any* unhandled exception, the system SHALL log error message, stack trace, and request ID using Loguru at ERROR level.

**Validates: Requirements 13.1, 13.5**

### Property 19: Database Retry Idempotence

*For any* transient database failure, retrying the same operation SHALL eventually succeed or return a deterministic permanent error after 3 attempts with exponential backoff.

**Validates: Requirements 19.3**

### Property 20: Workspace Data Isolation

*For any* two different workspaces, querying documents, chunks, or chat history SHALL never return data from the other workspace.

**Validates: Requirements 2.1-2.7 (implicit workspace isolation)**

---

**Note on Property-Based Testing Configuration:**

All properties SHALL be implemented using Hypothesis (Python) or fast-check (TypeScript) with minimum 100 iterations per test. Each property test SHALL be tagged with:

```python
# Feature: engineering-intelligence-hub-foundation, Property N: [property title]
```

This enables traceability from design properties to test implementations.

## Architecture Decision Records

### ADR-001: Monolithic Architecture

**Context**: Need to balance production-quality demonstration with solo developer maintainability.

**Decision**: Implement as monolithic application with single FastAPI backend and Next.js frontend.

**Rationale**:
- Simpler deployment (single docker-compose)
- Easier debugging and development
- Sufficient for 100 concurrent users
- Can refactor to microservices if needed
- Reduces operational complexity

**Consequences**:
- ✅ Faster development
- ✅ Simpler deployment
- ✅ Lower resource requirements
- ❌ Limited horizontal scaling
- ❌ Cannot scale components independently

**Alternatives Considered**: Microservices (rejected: over-engineering for portfolio project)

---

### ADR-002: PostgreSQL + pgvector vs Dedicated Vector DB

**Context**: Need vector storage for embeddings with relational data for users, workspaces, documents.

**Decision**: Use PostgreSQL with pgvector extension as unified database.

**Rationale**:
- Single database simplifies operations
- pgvector sufficient for 10M vectors
- ACID guarantees for all data
- Mature backup/restore tooling
- Lower cost (no separate service)

**Consequences**:
- ✅ Unified data model
- ✅ Simpler operations
- ✅ Lower infrastructure cost
- ❌ Slightly slower vector search than dedicated DB (acceptable for MVP)
- ❌ Limited to PostgreSQL ecosystem

**Alternatives Considered**:
- Pinecone: Rejected (requires paid API, vendor lock-in)
- Weaviate/Qdrant: Rejected (additional service complexity)

---

### ADR-003: Ollama for LLM Inference

**Context**: Need LLM for RAG answer generation, evaluation, query rewriting.

**Decision**: Use Ollama with local qwen3:8b or llama3.1:8b models.

**Rationale**:
- Zero API costs
- Privacy-friendly (no external data sharing)
- Docker-deployable
- Good quality from 8B models
- Demonstrates AI Engineering without cloud dependencies

**Consequences**:
- ✅ No ongoing costs
- ✅ Complete privacy
- ✅ Predictable performance
- ❌ Lower quality than GPT-4
- ❌ Requires GPU for fast inference (optional, works on CPU)

**Alternatives Considered**:
- OpenAI API: Rejected (ongoing costs, external dependency)
- Anthropic Claude: Rejected (same concerns)

---

### ADR-004: FastAPI Background Tasks vs Message Queue

**Context**: Need async document processing without blocking API responses.

**Decision**: Use FastAPI BackgroundTasks for document processing.

**Rationale**:
- Built into FastAPI
- Sufficient for 100 pages/minute throughput
- No additional infrastructure
- Failures logged in database
- Can upgrade to Celery later if needed

**Consequences**:
- ✅ Zero additional infrastructure
- ✅ Simpler deployment
- ✅ Sufficient for MVP scale
- ❌ No distributed task execution
- ❌ Tasks lost on server restart (acceptable for MVP)

**Alternatives Considered**:
- Celery + Redis: Rejected (over-engineering, additional services)
- RabbitMQ: Rejected (additional complexity)

---

### ADR-005: BAAI/bge-small-en-v1.5 Embedding Model

**Context**: Need fast, quality embeddings for semantic search.

**Decision**: Use BAAI/bge-small-en-v1.5 (384-dim, 133M params).

**Rationale**:
- Small model size (fast inference)
- Good quality for English
- Compact vectors (384-dim vs 768/1536)
- Open source, HuggingFace available
- ~50ms per embedding on CPU

**Consequences**:
- ✅ Fast inference
- ✅ Lower storage (384-dim)
- ✅ Good English quality
- ❌ English-only
- ❌ Lower quality than large models (acceptable tradeoff)

**Alternatives Considered**:
- OpenAI ada-002: Rejected (API costs)
- all-MiniLM-L6-v2: Rejected (slightly lower quality)

---

### ADR-006: LangGraph for Self-Healing RAG

**Context**: Need agentic workflow for self-healing RAG with state management.

**Decision**: Use LangGraph for agent orchestration.

**Rationale**:
- Purpose-built for agentic workflows
- Clear state machine model
- Observability built-in
- Active maintenance
- Good documentation

**Consequences**:
- ✅ Clear agent structure
- ✅ State persistence
- ✅ Easy to visualize workflow
- ❌ Additional dependency
- ❌ Learning curve

**Alternatives Considered**:
- Custom implementation: Rejected (reinventing wheel)
- LangChain: Rejected (too heavyweight, less control)

---

### ADR-007: Docker Compose vs Kubernetes

**Context**: Need container orchestration for deployment.

**Decision**: Use Docker Compose for all deployments.

**Rationale**:
- Solo developer project
- Single-server deployment sufficient
- Simpler than Kubernetes
- Easy local development
- Railway/Render support docker-compose

**Consequences**:
- ✅ Simple deployment
- ✅ Easy local dev
- ✅ Lower learning curve
- ❌ No auto-scaling
- ❌ Single point of failure

**Alternatives Considered**:
- Kubernetes: Rejected (massive over-engineering for portfolio)
- Docker Swarm: Rejected (Docker Compose sufficient)

---

### ADR-008: JWT Stateless Authentication

**Context**: Need secure authentication with scalability potential.

**Decision**: Use stateless JWT tokens with HS256, 24-hour expiration.

**Rationale**:
- No server-side session storage
- Scales horizontally without session stickiness
- Industry standard
- Works with mobile/web clients
- Simple to implement

**Consequences**:
- ✅ Stateless (scalable)
- ✅ Simple implementation
- ✅ Standard approach
- ❌ Cannot revoke tokens before expiration
- ❌ Token refresh not implemented in MVP

**Alternatives Considered**:
- Session cookies: Rejected (requires session store)
- OAuth2: Rejected (over-engineering for MVP)

## Deployment Considerations

### Railway Deployment

**Advantages**:
- Simple Git-based deployments
- PostgreSQL add-on with pgvector support
- Automatic HTTPS
- Environment variable management
- Free tier for development

**Configuration**:
```yaml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
```

**Limitations**:
- Ollama requires GPU plan (higher cost)
- 500MB memory limit on free tier
- Limited to single region

---

### Render Deployment

**Advantages**:
- PostgreSQL with native pgvector support
- Docker Compose support
- Free tier for database
- Automatic SSL
- Easy rollbacks

**Configuration**:
```yaml
services:
  - type: web
    name: backend
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: engineering-hub-db
          property: connectionString
```

**Limitations**:
- Ollama inference may be slow on CPU-only instances
- Cold starts on free tier
- Limited concurrent connections on free tier

---

### Simplified Deployment for Portfolio

**Recommended Approach**:
1. **Local Development**: Full Docker Compose with Ollama
2. **Demo/Portfolio**: Deploy to Railway/Render with:
   - Backend API + Database (deployed)
   - Frontend (deployed)
   - Ollama (run locally or use CPU mode)
   - Demo video showing full system

**Justification**: Portfolio reviewers care about code quality and architecture, not 24/7 uptime. Recording demonstration shows system working end-to-end without ongoing hosting costs.

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Core infrastructure and authentication

**Deliverables**:
- PostgreSQL + pgvector setup
- User registration/login (JWT)
- Protected route middleware
- Database models and migrations
- Basic error handling and logging
- Docker Compose configuration
- CI/CD pipeline setup

**Success Criteria**:
- Users can register and login
- JWT auth working on protected routes
- All tests passing
- Docker Compose starts all services

---

### Phase 2: Document Ingestion (Weeks 3-4)

**Goal**: Upload and process documents

**Deliverables**:
- File upload API
- PDF/DOCX/TXT/Markdown extraction
- Text chunking (512 tokens, 50 overlap)
- Embedding generation (BAAI/bge-small)
- pgvector storage
- Background processing
- Document status tracking

**Success Criteria**:
- 100+ pages/minute throughput
- Correct chunking and embedding storage
- Status tracking (pending → processing → indexed/failed)
- All unit tests passing

---

### Phase 3: Workspace Management (Week 5)

**Goal**: Multi-tenant workspace support

**Deliverables**:
- Workspace CRUD operations
- Member invitation and management
- Role-based access control (Owner/Member)
- Workspace data isolation
- Authorization middleware

**Success Criteria**:
- Users can create/join multiple workspaces
- Owners can manage members
- Data isolation verified
- Authorization tests passing

---

### Phase 4: RAG Pipeline (Weeks 6-7)

**Goal**: Semantic search and basic RAG

**Deliverables**:
- Semantic search (cosine similarity)
- Reranking (BAAI/bge-reranker)
- Ollama integration
- RAG pipeline (retrieve → generate)
- Citation generation
- Chat history management

**Success Criteria**:
- Search latency < 2s (95th percentile)
- RAG latency < 5s (95th percentile)
- Citations include source references
- Chat history preserved

---

### Phase 5: GitHub Integration (Week 8)

**Goal**: Repository analysis

**Deliverables**:
- GitHub repository cloning
- Documentation extraction
- Structure analysis
- Repository overview generation
- Integration with document pipeline

**Success Criteria**:
- Public repos can be cloned and analyzed
- Documentation extracted correctly
- Overview generated automatically
- Temp files cleaned up

---

### Phase 6: Self-Healing RAG (Weeks 9-10)

**Goal**: Agentic quality improvement

**Deliverables**:
- LangGraph state machine
- Retriever Agent
- Generator Agent
- Critic Agent (faithfulness, relevance)
- Query Rewriter Agent
- 2-iteration feedback loop

**Success Criteria**:
- Self-healing improves answer quality
- Max 2 iterations enforced
- Quality scores calculated
- State transitions logged

---

### Phase 7: Evaluation System (Week 11)

**Goal**: Quality metrics and dashboard

**Deliverables**:
- Faithfulness calculation (LLM-based)
- Relevance scoring
- Context precision/recall
- Latency tracking
- Token cost estimation
- Evaluation dashboard UI
- Time-series visualization

**Success Criteria**:
- Metrics calculated for all queries
- Dashboard displays 7-day trends
- Async metric computation doesn't block responses

---

### Phase 8: Frontend Polish (Week 12)

**Goal**: Complete UI/UX

**Deliverables**:
- Responsive design (TailwindCSS)
- Loading states and error messages
- Document upload progress
- Chat interface with citations
- Search interface
- Workspace management UI
- Dashboard visualizations

**Success Criteria**:
- All features accessible via UI
- Mobile-responsive
- Accessibility (WCAG AA basics)
- E2E tests passing

---

### Phase 9: Testing & Quality (Week 13)

**Goal**: Comprehensive test coverage

**Deliverables**:
- Unit tests (70%+ backend, 60%+ frontend)
- Integration tests
- E2E tests (Playwright)
- Property-based tests (Hypothesis)
- Load testing
- Security testing

**Success Criteria**:
- Coverage targets met
- All critical paths tested
- Performance targets met
- No critical security issues

---

### Phase 10: Documentation & Deployment (Week 14)

**Goal**: Production-ready deployment

**Deliverables**:
- README with setup instructions
- API documentation (OpenAPI)
- Architecture documentation
- Deployment guide
- Demo video
- Railway/Render deployment
- Monitoring setup (Prometheus/Grafana)

**Success Criteria**:
- Complete documentation
- One-command local setup
- Deployed to production
- Demo video recorded
- Portfolio-ready

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-15 | AI Agent | Initial technical design document |

---

## Summary

This technical design provides a comprehensive blueprint for the Engineering Intelligence Hub Foundation—a production-quality AI SaaS platform optimized for solo developer implementation. The design balances:

- **Production Patterns**: RAG, agentic AI, evaluation metrics, proper auth/authorization
- **Practical Constraints**: Monolithic architecture, open-source only, Docker Compose deployment
- **Portfolio Value**: Demonstrates AI Engineering expertise without enterprise complexity

Key architectural decisions prioritize simplicity and maintainability while preserving demonstration value for job applications. The 14-week implementation plan provides clear milestones from foundation through deployment.

Next steps: Review and approval of design document, then proceed to task breakdown and implementation.
