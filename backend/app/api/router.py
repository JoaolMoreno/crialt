from fastapi import APIRouter, Depends

from app.api import auth, users, clients, projects, stages, files, tasks
from app.api.dependencies import admin_required, client_resource_permission

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router,
                          prefix="/users",
                          tags=["users"],
                          #dependencies=[Depends(admin_required)]
                          )
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(stages.router, prefix="/stages", tags=["stages"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
