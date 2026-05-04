"""API routes module."""

from fastapi import APIRouter

from app.api.routes.api_keys.router import router as api_keys_router
from app.api.routes.api_workflows.router import router as api_workflows_router
from app.api.routes.auth.router import router as auth_router
from app.api.routes.health.router import router as health_router
from app.api.routes.integration_apis.router import router as integration_apis_router
from app.api.routes.pipelines.router import router as pipelines_router
from app.api.routes.process_now.router import router as process_now_router
from app.api.routes.tasks.router import router as tasks_router
from app.api.routes.users.router import router as users_router

# Private/internal APIs
router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(api_keys_router)
router.include_router(pipelines_router)
router.include_router(tasks_router)
router.include_router(users_router)
router.include_router(process_now_router)

# Third-party APIs
subapprouter = APIRouter(tags=["Third party Integrations"])
subapprouter.include_router(integration_apis_router)
subapprouter.include_router(api_workflows_router)

# Main router
main_router = APIRouter(prefix="/api")
main_router.include_router(router, include_in_schema=False)  # hidden in docs
main_router.include_router(subapprouter)  # visible in docs
