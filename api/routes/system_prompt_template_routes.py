# NUEVO ARCHIVO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from core.database import get_db
from core import models as db_models
from schemas import prompt_schemas
from crud import prompt_crud
# from api.dependencies import get_current_active_user # No se necesita para plantillas globales, a menos que se quiera proteger

router = APIRouter(prefix="/system-prompt-templates", tags=["System Prompt Templates (Global)"])

@router.get("/", response_model=List[prompt_schemas.SystemPromptTemplateResponse])
async def read_system_prompt_templates(
    content_module: Optional[str] = Query(None, description="Filtrar por módulo: 'linkedin' o 'blog'"),
    article_type: Optional[str] = Query(None, description="Filtrar por tipo de artículo para blog: 'general_interest' o 'success_case'"),
    style_key: Optional[str] = Query(None, description="Filtrar por clave de estilo: 'Default', 'Pablo', etc."),
    db: Session = Depends(get_db)
    # current_user: db_models.User = Depends(get_current_active_user) # Opcional si se quiere proteger
):
    """
    Obtiene una lista de plantillas de system prompt base globales, opcionalmente filtradas.
    Estas son las plantillas predefinidas por el administrador.
    """
    templates = prompt_crud.get_system_prompt_templates(
        db, 
        content_module=content_module, 
        article_type=article_type,
        style_key=style_key
    )
    return templates

# Podrías añadir endpoints POST, PUT, DELETE aquí si quisieras una API para administrar
# estas plantillas base, pero requerirían autenticación y autorización de administrador.
# Por ahora, asumimos que se llenan mediante un script de seeding o manualmente.