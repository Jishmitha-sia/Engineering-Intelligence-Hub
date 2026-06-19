# Changelog

All notable changes to the Engineering Intelligence Hub project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (19-06-2026)
- **Phase 1 Backend**: FastAPI app, JWT auth, user model, Alembic migration, security unit tests
- **Phase 1 Frontend**: Next.js 14 login/register, AuthContext, protected dashboard
- **Infrastructure**: Docker Compose (postgres, backend, frontend), `.gitignore`, `.env.example`
- **Documentation**: Reorganized all `.md` files into `docs/` folder; added `docs/setup.md` manual testing guide

### Planned
- Phase 2: Workspace Management
- Phase 3: Document Ingestion Pipeline
- Phase 4: RAG Chat Implementation
- Phase 5: GitHub Integration
- Phase 6: Self-Healing RAG with LangGraph
- Phase 7: Evaluation System and Metrics
- Phase 8: Analytics and Monitoring
- Phase 9: Production Engineering
- Phase 10: Testing and Deployment

## [0.1.0] - 2026-06-18

### Added
- **Project Structure**: Initial repository setup and folder structure
- **Requirements Document**: Comprehensive requirements specification with 20 functional and non-functional requirements
- **Technical Design Document**: Complete system architecture, database schema, API design, and deployment strategy
- **Task Breakdown**: Detailed 10-phase implementation plan with 50+ tasks
- **Documentation**: README, Architecture Decision Records (ADRs), and project state tracking

### Architecture Decisions
- **ADR-001**: Monolithic architecture over microservices for simplicity
- **ADR-002**: PostgreSQL + pgvector over specialized vector databases
- **ADR-003**: Ollama for local LLM inference over paid APIs
- **ADR-004**: FastAPI backend framework over Flask/Django
- **ADR-005**: Next.js frontend over React SPA
- **ADR-006**: JWT authentication over session-based auth
- **ADR-007**: Docker Compose over Kubernetes for deployment
- **ADR-008**: BAAI BGE models for embeddings and reranking
- **ADR-009**: LangGraph over LangChain for agentic workflows
- **ADR-010**: FastAPI BackgroundTasks over message queues
- **ADR-011**: TailwindCSS + shadcn/ui for styling
- **ADR-012**: Prometheus + Grafana for monitoring

### Technical Specifications
- **Tech Stack**: FastAPI + Next.js + PostgreSQL + Ollama
- **Database Schema**: 9 tables with pgvector for embeddings
- **API Design**: RESTful with versioning and standardized responses
- **Authentication**: JWT with bcrypt password hashing
- **AI Models**: BAAI/bge-small-en-v1.5 (embeddings), BAAI/bge-reranker-base (reranking), Ollama qwen3:8b/llama3.1:8b (LLM)

### Project Management
- **Repository**: https://github.com/Jishmitha-sia/Engineering-Intelligence-Hub.git
- **Target**: 80% production-level AI SaaS platform
- **Timeline**: 14-week implementation plan
- **Scope**: Monolithic, Docker Compose-based, open-source only

## Phase Implementation History

### Phase 0: Planning and Design ✅ [Completed: 2026-06-18]

#### Added
- Project vision and goals definition
- User persona analysis (Software Engineer, Engineering Manager, Portfolio Reviewer)
- Functional requirements (20 requirements with EARS-format acceptance criteria)
- Non-functional requirements (performance, security, scalability)
- Technical architecture design
- Database schema with pgvector integration
- API endpoint specifications
- Component architecture and interfaces
- Deployment architecture
- Task dependency graph

#### Design Highlights
- **High-Level Architecture**: 3-tier monolithic design
- **Database**: PostgreSQL 15 with pgvector extension for unified relational + vector storage
- **Backend Structure**: Modular FastAPI with services, models, schemas, agents, and utilities
- **Frontend Structure**: Next.js 14 App Router with component-based architecture
- **Agentic Workflows**: LangGraph state machine for self-healing RAG
- **Evaluation System**: Faithfulness, Relevance, Context Precision/Recall metrics

#### Performance Targets Established
- Search latency: < 2 seconds (95th percentile)
- RAG latency: < 5 seconds (95th percentile)
- Document processing: 100+ pages per minute
- Answer faithfulness: > 0.7 average
- System uptime: > 95%

#### Scalability Targets Defined
- 1000 registered users
- 100 concurrent users
- 100,000 documents
- 10 million chunks/embeddings

---

## Upcoming Phases

### Phase 1: Foundation [Planned: Week 1-2]
- [ ] Backend project setup (FastAPI)
- [ ] Database setup (PostgreSQL + pgvector)
- [ ] User authentication (JWT + bcrypt)
- [ ] Frontend project setup (Next.js)
- [ ] Docker Compose configuration
- [ ] Basic CI/CD pipeline

### Phase 2: Workspace Management [Planned: Week 3]
- [ ] Multi-tenant workspace models
- [ ] Owner/Member role system
- [ ] Workspace CRUD operations
- [ ] Authorization middleware
- [ ] Workspace management UI

### Phase 3: Document Ingestion [Planned: Week 4]
- [ ] File upload API (PDF, DOCX, TXT, Markdown)
- [ ] Text extraction pipeline
- [ ] Chunking algorithm (512 tokens, 50 overlap)
- [ ] Embedding generation (BAAI/bge-small)
- [ ] Background processing
- [ ] Document management UI

### Phase 4: RAG Chat [Planned: Week 5-6]
- [ ] Vector search (pgvector cosine similarity)
- [ ] Reranking pipeline (BAAI/bge-reranker)
- [ ] Ollama LLM integration
- [ ] RAG pipeline orchestration
- [ ] Citation generation
- [ ] Chat interface UI

### Phase 5: GitHub Integration [Planned: Week 7]
- [ ] Repository cloning
- [ ] Documentation extraction
- [ ] Structure analysis
- [ ] Repository overview generation

### Phase 6: Self-Healing RAG [Planned: Week 8-9]
- [ ] LangGraph state machine
- [ ] Retriever Agent
- [ ] Generator Agent
- [ ] Critic Agent (quality evaluation)
- [ ] Query Rewriter Agent
- [ ] Feedback loop implementation

### Phase 7: Evaluation System [Planned: Week 10]
- [ ] Faithfulness calculation
- [ ] Relevance scoring
- [ ] Context precision/recall metrics
- [ ] Evaluation dashboard UI

### Phase 8: Analytics & Monitoring [Planned: Week 11]
- [ ] Usage analytics dashboard
- [ ] Prometheus metrics
- [ ] Grafana dashboards

### Phase 9: Production Engineering [Planned: Week 12]
- [ ] Rate limiting
- [ ] Enhanced logging (Loguru)
- [ ] Error handling
- [ ] Security hardening

### Phase 10: Testing & Deployment [Planned: Week 13-14]
- [ ] Comprehensive test suite (70%+ backend, 60%+ frontend)
- [ ] E2E testing (Playwright)
- [ ] CI/CD pipeline
- [ ] Production deployment
- [ ] Documentation completion

---

## Development Conventions

### Version Numbering
- **Major.Minor.Patch** (Semantic Versioning)
- **Major**: Breaking changes or major feature releases
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, small improvements

### Change Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

### Git Workflow
- **Main Branch**: Production-ready code
- **Feature Branches**: Individual feature development
- **Release Branches**: Release preparation
- **Hotfix Branches**: Critical fixes

### Documentation Updates
- All changes must update relevant documentation
- ADRs for architectural decisions
- README for setup instructions
- API documentation for endpoint changes

---

## Contributing Guidelines

### Change Documentation
1. Update this CHANGELOG.md for all notable changes
2. Follow the established format and categories
3. Include relevant issue/PR references
4. Update version numbers according to semantic versioning

### Review Process
- All changes require PR review
- Breaking changes require architecture review
- Documentation updates included in PR
- Tests passing before merge

---

## Release Process

### Pre-Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number bumped
- [ ] Migration scripts tested
- [ ] Performance targets verified

### Release Steps
1. Create release branch
2. Update version numbers
3. Generate release notes from CHANGELOG
4. Create GitHub release
5. Deploy to production
6. Monitor metrics and logs

---

## Support and Maintenance

### Long-Term Support
- **Current Version**: Active development and bug fixes
- **Previous Version**: Security fixes only
- **Older Versions**: Community support only

### Update Policy
- **Security Patches**: Immediate release
- **Bug Fixes**: Next minor release
- **New Features**: Next major/minor release

---

**Project Repository**: https://github.com/Jishmitha-sia/Engineering-Intelligence-Hub.git  
**Maintainer**: AI Development Team  
**Last Updated**: 19 June 2026