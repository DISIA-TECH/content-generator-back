# (Se mantiene prácticamente igual, solo asegurándose de que el router de API se incluye correctamente)
# (Y que el prefijo API_V1_STR se aplique correctamente)

from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from core.logger import app_logger 
# MODIFICADO: Importar el api_router real desde su ubicación.
from api.router import api_router # Asumiendo que tienes api/router.py

# --- ELIMINADO: Bloque de simulación de api/router.py ---

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" 
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas API principales (que a su vez incluyen las de LinkedIn, Blog, etc.)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    app_logger.info("Iniciando aplicación...")
    if not settings.OPENAI_API_KEY:
        app_logger.warning("API Key de OpenAI no configurada. Algunas funcionalidades pueden no estar disponibles.")
    else:
        app_logger.info("API Key de OpenAI encontrada.")
    app_logger.info(f"Aplicación configurada para ejecutarse en: {settings.HOST}:{settings.PORT}")
    app_logger.info(f"Ruta OpenAPI JSON disponible en: {settings.API_V1_STR}/openapi.json")
    app_logger.info(f"Ruta de la UI de Docs (Swagger) disponible en: {settings.API_V1_STR}/docs")
    app_logger.info(f"Ruta de la UI de ReDoc disponible en: {settings.API_V1_STR}/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("Cerrando aplicación...")


@app.get("/") 
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {
        "status": "online",
        "message": f"Bienvenido a {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}",
        "docs_url": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health", tags=["Health Check"])
async def health_check_root():
    return {"status": "healthy", "service": settings.PROJECT_NAME}


# --- Inicio: Código de Debug para Rutas ---
from fastapi.routing import APIRoute
print("="*80)
print("RUTAS REGISTRADAS EN LA APLICACIÓN FASTAPI:")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"Path: {route.path}, Name: {route.name}, Methods: {list(route.methods)}")
    elif hasattr(route, 'path'): # Para Mounts/Routers que no son APIRoute directamente
         print(f"Router/Mount Path: {route.path}")
         if hasattr(route, 'routes'):
             for sub_route in route.routes:
                 if isinstance(sub_route, APIRoute):
                     print(f"  Sub-Path: {sub_route.path}, Name: {sub_route.name}, Methods: {list(sub_route.methods)}")
print("="*80)
# --- Fin: Código de Debug para Rutas ---


if __name__ == "__main__":
    """Punto de entrada para ejecutar la aplicación con uvicorn."""
    uvicorn.run(
        "api.main:app", 
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower() 
    )

