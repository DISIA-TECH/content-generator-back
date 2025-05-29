from fastapi import APIRouter

from blog.api.routes import router as blog_router
from linkedin.api.routes import router as linkedin_router
from api.routes import auth_routes, user_routes, history_routes

# NUEVAS IMPORTACIONES para las rutas de prompts
from api.routes import system_prompt_template_routes # Router para plantillas base
from api.routes import user_custom_prompt_routes # Router para plantillas personalizadas del usuario
from core.config import settings # Importar settings para el prefijo de system_prompt_templates

api_router = APIRouter()

# Rutas de autenticación y usuarios (ya tienen sus propios prefijos /auth y /users)
api_router.include_router(auth_routes.router) 
api_router.include_router(user_routes.router) 

# Rutas de historial (ya tiene su propio prefijo /me/history)
api_router.include_router(history_routes.router)

# Rutas específicas de módulos (LinkedIn y Blog ya tienen sus prefijos)
api_router.include_router(blog_router) 
api_router.include_router(linkedin_router) 

# NUEVOS ROUTERS PARA PROMPTS
# Las plantillas base globales no están bajo /me/
api_router.include_router(system_prompt_template_routes.router) # Este ya tiene prefix="/system-prompt-templates"
# Las plantillas personalizadas del usuario sí están bajo /me/
api_router.include_router(user_custom_prompt_routes.router) # Este ya tiene prefix="/me/custom-prompts"


# Los routers para tags se añadirán después
# from api.routes import tag_routes
# api_router.include_router(tag_routes.router)