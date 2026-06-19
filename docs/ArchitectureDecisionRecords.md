# Architecture Decision Records (ADR)

## Engineering Intelligence Hub - Technical Decisions

**Project**: AI-powered engineering knowledge platform  
**Repository**: https://github.com/Jishmitha-sia/Engineering-Intelligence-Hub.git  
**Last Updated**: 19 June 2026

---

## ADR-001: Monolithic Architecture over Microservices

**Date**: June 18, 2026  
**Status**: Accepted  
**Deciders**: AI Agent, Project Owner  

### Context
Need to choose between monolithic and microservices architecture for an AI SaaS platform targeting 80% production quality as a portfolio project.

### Decision
We will use a **monolithic architecture** with clear internal module separation.

### Rationale
**Chosen**: Monolithic
- ✅ Simpler deployment (Docker Compose vs Kubernetes)
- ✅ Easier debugging and development
- ✅ Lower operational complexity
- ✅ Suitable for solo developer maintenance
- ✅ Faster development cycle
- ✅ Single codebase for portfolio demonstration

**Rejected**: Microservices
- ❌ Complex deployment orchestration
- ❌ Service mesh complexity
- ❌ Distributed systems challenges
- ❌ Overkill for portfolio project
- ❌ Higher maintenance overhead

### Consequences
- Faster initial development
- Simpler deployment pipeline
- Easier local development setup
- Future scaling may require architectural evolution

---

## ADR-002: PostgreSQL + pgvector over Specialized Vector Databases

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need to store both relational data (users, workspaces, documents) and vector embeddings for semantic search.

### Decision
We will use **PostgreSQL 15+ with pgvector extension** as unified data store.

### Rationale
**Chosen**: PostgreSQL + pgvector
- ✅ Single database for relational + vector data
- ✅ Mature, battle-tested reliability
- ✅ ACID transactions across data types
- ✅ Familiar SQL interface
- ✅ Excellent Docker support
- ✅ Cost-effective (no specialized DB licensing)

**Rejected**: Separate Vector DB (Pinecone, Weaviate, Chroma)
- ❌ Additional infrastructure complexity
- ❌ Data consistency challenges
- ❌ Multiple database connections
- ❌ Higher operational overhead
- ❌ Vendor lock-in (for managed services)

### Consequences
- Simplified data architecture
- Single backup/restore process
- Potential vector search performance trade-offs vs specialized DBs
- Easier local development

---

## ADR-003: Ollama over Paid LLM APIs

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need LLM inference for RAG answer generation, evaluation, and agentic workflows.

### Decision
We will use **Ollama for local LLM inference** with qwen3:8b and llama3.1:8b models.

### Rationale
**Chosen**: Ollama (Local LLMs)
- ✅ No API costs or usage limits
- ✅ Privacy-friendly (data stays local)
- ✅ Offline capability
- ✅ Consistent performance (no rate limits)
- ✅ Portfolio demonstration without API keys
- ✅ Good 8B model quality for demonstration

**Rejected**: Paid APIs (OpenAI, Anthropic, etc.)
- ❌ Ongoing API costs
- ❌ Rate limiting and quotas
- ❌ Privacy concerns for document data
- ❌ Internet dependency
- ❌ API key management complexity

### Consequences
- Higher hardware requirements (8GB+ RAM)
- Potentially lower quality vs GPT-4
- Self-hosted inference responsibility
- Simplified cost structure

---

## ADR-004: FastAPI over Flask/Django for Backend

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need Python web framework for AI/ML backend with async support and automatic API documentation.

### Decision
We will use **FastAPI** as the backend framework.

### Rationale
**Chosen**: FastAPI
- ✅ Native async/await support
- ✅ Automatic OpenAPI/Swagger documentation
- ✅ Pydantic integration for type safety
- ✅ High performance (comparable to Node.js)
- ✅ Modern Python ecosystem alignment
- ✅ Excellent developer experience

**Rejected**: Flask
- ❌ Limited async support
- ❌ Manual API documentation
- ❌ More boilerplate code

**Rejected**: Django
- ❌ Heavy framework for API-only backend
- ❌ ORM coupling (prefer SQLAlchemy)
- ❌ Less suitable for ML/AI workloads

### Consequences
- Fast development of async APIs
- Automatic API documentation
- Type safety throughout codebase
- Learning curve for FastAPI-specific patterns

---

## ADR-005: Next.js over React SPA for Frontend

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need modern React-based frontend with TypeScript support and good developer experience.

### Decision
We will use **Next.js 14 with App Router** for the frontend.

### Rationale
**Chosen**: Next.js
- ✅ Built-in SSR/SSG capabilities
- ✅ Excellent TypeScript support
- ✅ File-based routing (App Router)
- ✅ Built-in optimization (images, fonts, etc.)
- ✅ Great developer experience
- ✅ Production-ready defaults

**Rejected**: Create React App (SPA)
- ❌ Client-only rendering
- ❌ Manual optimization required
- ❌ No built-in routing
- ❌ Less SEO-friendly

**Rejected**: Vue.js/Nuxt
- ❌ Smaller ecosystem for AI/ML tools
- ❌ Less familiar for most developers

### Consequences
- Better SEO and initial page load
- More complex deployment (SSR considerations)
- Full-stack React development patterns
- Bundle size optimization out of the box

---

## ADR-006: JWT over Session-Based Authentication

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need authentication mechanism for API-first architecture with frontend/backend separation.

### Decision
We will use **JWT (JSON Web Tokens)** for authentication.

### Rationale
**Chosen**: JWT
- ✅ Stateless authentication
- ✅ Works well with API architecture
- ✅ Scales without server-side session storage
- ✅ Frontend/backend decoupling
- ✅ Standard, well-understood approach

**Rejected**: Session-based auth
- ❌ Requires server-side session store
- ❌ Scaling challenges
- ❌ Less suitable for API-first architecture

### Consequences
- Stateless scalability
- Token expiration management required
- Secure storage considerations (httpOnly cookies vs localStorage)
- Cannot easily revoke specific tokens

---

## ADR-007: Docker Compose over Kubernetes for Deployment

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need container orchestration for local development and production deployment.

### Decision
We will use **Docker Compose** for both development and production deployment.

### Rationale
**Chosen**: Docker Compose
- ✅ Simple, declarative service definition
- ✅ Suitable for single-machine deployment
- ✅ Easy local development setup
- ✅ Minimal learning curve
- ✅ Sufficient for portfolio project scale

**Rejected**: Kubernetes
- ❌ Unnecessary complexity for project scale
- ❌ High operational overhead
- ❌ Expensive hosting requirements
- ❌ Overengineered for demo/portfolio use

### Consequences
- Simple deployment process
- Limited to single-machine scaling
- Easy local development environment
- May need evolution for true production scale

---

## ADR-008: BAAI BGE Models for Embeddings and Reranking

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need embedding model for semantic search and reranking model for result quality.

### Decision
We will use **BAAI/bge-small-en-v1.5** for embeddings and **BAAI/bge-reranker-base** for reranking.

### Rationale
**Chosen**: BAAI BGE Models
- ✅ Good quality-to-size ratio (bge-small: 133M parameters)
- ✅ Fast inference suitable for real-time search
- ✅ Good English language performance
- ✅ Active development and community
- ✅ Free and open-source
- ✅ Compatible with sentence-transformers

**Rejected**: OpenAI text-embedding-ada-002
- ❌ API costs and rate limits
- ❌ Internet dependency

**Rejected**: Larger models (bge-large)
- ❌ Higher memory requirements
- ❌ Slower inference for real-time use

### Consequences
- Fast, cost-effective embedding generation
- Good search quality for English documents
- Self-hosted inference control
- Memory and compute requirements under control

---

## ADR-009: LangGraph over LangChain for Agentic Workflows

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need framework for implementing self-healing RAG with multiple agents and state management.

### Decision
We will use **LangGraph** for agentic workflow orchestration.

### Rationale
**Chosen**: LangGraph
- ✅ Explicit state machine design
- ✅ Better observability and debugging
- ✅ Cyclic workflow support (feedback loops)
- ✅ Built-in state persistence
- ✅ Designed for multi-agent systems
- ✅ Better control over execution flow

**Rejected**: Pure LangChain
- ❌ More linear, chain-based approach
- ❌ Limited cyclic workflow support
- ❌ Less explicit state management

**Rejected**: Custom implementation
- ❌ Reinventing workflow orchestration
- ❌ More development time
- ❌ Missing observability features

### Consequences
- Robust agentic workflow implementation
- Learning curve for LangGraph patterns
- Better debugging and observability
- Framework dependency for agent coordination

---

## ADR-010: Background Tasks over Message Queues for Document Processing

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need asynchronous processing for document ingestion (text extraction, chunking, embedding).

### Decision
We will use **FastAPI BackgroundTasks** for async document processing.

### Rationale
**Chosen**: FastAPI BackgroundTasks
- ✅ Built into FastAPI framework
- ✅ No additional infrastructure required
- ✅ Suitable for portfolio project scale
- ✅ Simple error handling and retry
- ✅ In-process task execution

**Rejected**: Message Queues (Redis, RabbitMQ, Kafka)
- ❌ Additional infrastructure complexity
- ❌ Overengineered for project scale
- ❌ More operational overhead
- ❌ Unnecessary for monolithic architecture

### Consequences
- Simpler architecture and deployment
- Limited to single-machine processing
- In-memory task queue (lost on restart)
- May need evolution for high-volume processing

---

## ADR-011: TailwindCSS + shadcn/ui over Component Libraries

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need UI styling approach and component system for consistent, professional frontend.

### Decision
We will use **TailwindCSS with shadcn/ui components**.

### Rationale
**Chosen**: TailwindCSS + shadcn/ui
- ✅ Utility-first CSS for rapid development
- ✅ Consistent design system
- ✅ Copy-paste components (no NPM dependency)
- ✅ Highly customizable
- ✅ Modern, professional appearance
- ✅ Excellent accessibility defaults

**Rejected**: Material-UI / Ant Design
- ❌ Larger bundle size
- ❌ Harder to customize deeply
- ❌ Framework-specific styling

**Rejected**: Custom CSS
- ❌ More development time
- ❌ Inconsistent design patterns
- ❌ Maintenance overhead

### Consequences
- Rapid UI development
- Professional, consistent appearance
- Learning curve for utility-first CSS
- Excellent mobile responsiveness

---

## ADR-012: Prometheus + Grafana for Monitoring

**Date**: June 18, 2026  
**Status**: Accepted  

### Context
Need monitoring and observability for production-level application demonstration.

### Decision
We will use **Prometheus for metrics collection** and **Grafana for visualization**.

### Rationale
**Chosen**: Prometheus + Grafana
- ✅ Industry-standard monitoring stack
- ✅ Excellent Docker Compose integration
- ✅ Rich ecosystem of exporters
- ✅ Powerful query language (PromQL)
- ✅ Beautiful dashboards and alerting
- ✅ Open-source and well-documented

**Rejected**: Cloud monitoring (DataDog, New Relic)
- ❌ Ongoing costs
- ❌ Vendor lock-in
- ❌ Less suitable for local development

**Rejected**: Simple logging only
- ❌ Limited observability
- ❌ No real-time metrics
- ❌ Poor production readiness demonstration

### Consequences
- Production-grade monitoring capabilities
- Additional containers in stack
- Rich observability for debugging
- Industry-standard skills demonstration

---

## Future Architecture Decisions

### Pending Decisions
- **Caching Strategy**: Redis vs in-memory vs none
- **File Storage**: Local volumes vs object storage for production
- **Search Analytics**: Custom vs third-party analytics
- **API Rate Limiting**: Implementation approach and storage

### Potential Evolution
- **Horizontal Scaling**: When/if to move beyond single-machine
- **Microservices Migration**: Conditions that would trigger decomposition
- **Cloud-Native Features**: Which cloud services to adopt for production
- **Performance Optimization**: Database query optimization strategies

---

## Decision Review Process

### Regular Reviews
- **Quarterly**: Review all accepted ADRs for continued relevance
- **Pre-Major Release**: Assess architectural fitness
- **Performance Issues**: Re-evaluate related architectural decisions

### Decision Criteria
1. **Simplicity**: Prefer simpler solutions for portfolio project
2. **Production Quality**: Demonstrate production-ready patterns
3. **Cost Effectiveness**: Minimize ongoing operational costs
4. **Developer Experience**: Optimize for development speed and debugging
5. **Scalability**: Consider future scaling without over-engineering
6. **Portfolio Value**: Showcase relevant skills for AI Engineer roles

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | June 18, 2026 | Initial ADR documentation with 12 key decisions |