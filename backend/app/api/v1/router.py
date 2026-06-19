"""
API v1 router aggregation for Engineering Intelligence Hub.

Combines all API v1 endpoints into a single router.
"""

from fastapi import APIRouter

from api.v1.auth import router as auth_router
# Future routers will be imported here:
# from api.v1.workspaces import router as workspaces_router  # Phase 2
# from api.v1.documents import router as documents_router    # Phase 3
# from api.v1.search import router as search_router          # Phase 4
# from api.v1.chat import router as chat_router              # Phase 4
# from api.v1.github import router as github_router          # Phase 5
# from api.v1.evaluation import router as evaluation_router  # Phase 7
# from api.v1.analytics import router as analytics_router    # Phase 8

# Create main API v1 router
api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth_router)

# Future routers will be included here:
# api_router.include_router(workspaces_router, prefix="/workspaces", tags=["Workspaces"])
# api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
# api_router.include_router(search_router, prefix="/search", tags=["Search"])
# api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
# api_router.include_router(github_router, prefix="/github", tags=["GitHub"])
# api_router.include_router(evaluation_router, prefix="/evaluation", tags=["Evaluation"])
# api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])