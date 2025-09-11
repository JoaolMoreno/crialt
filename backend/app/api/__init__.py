"""
API Routes Module
Centraliza todas as rotas da API REST
"""

from .router import api_router
from .dependencies import get_db, get_current_user, get_current_actor, client_resource_permission, get_current_actor_factory

__all__ = [
    "get_db",
    "get_current_user",
    "get_current_actor",
    "client_resource_permission",
    "get_current_actor_factory",
    "api_router"
]