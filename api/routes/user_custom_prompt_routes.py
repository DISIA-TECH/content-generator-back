# NUEVO ARCHIVO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from core.database import get_db
from core import models as db_models
from schemas import prompt_schemas
from crud import prompt_crud
from api.dependencies import get_current_active_user

router = APIRouter(prefix="/me/custom-prompts", tags=["User Custom Prompts"])

@router.post("/", response_model=prompt_schemas.UserCustomPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_my_custom_prompt(
    prompt_data: prompt_schemas.UserCustomPromptCreate,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Crea una nueva plantilla de system prompt personalizada para el usuario actual.
    """
    # Validar content_module y article_type si es necesario
    if prompt_data.content_module not in ['linkedin', 'blog']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Módulo de contenido inválido.")
    if prompt_data.content_module == 'blog' and prompt_data.article_type not in ['general_interest', 'success_case', None]:
         # Permitir None para article_type si el módulo es blog pero no es específico, o ajustar la lógica
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de artículo inválido para blog.")
    if prompt_data.content_module == 'linkedin' and prompt_data.article_type is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de artículo no aplica para LinkedIn.")

    return prompt_crud.create_user_custom_prompt(db=db, user_id=current_user.user_id, prompt_data=prompt_data)

@router.get("/", response_model=List[prompt_schemas.UserCustomPromptResponse])
async def read_my_custom_prompts(
    content_module: Optional[str] = Query(None, description="Filtrar por módulo: 'linkedin' o 'blog'"),
    article_type: Optional[str] = Query(None, description="Filtrar por tipo de artículo para blog: 'general_interest' o 'success_case'"),
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Obtiene todas las plantillas de system prompt personalizadas para el usuario actual,
    opcionalmente filtradas.
    """
    prompts = prompt_crud.get_user_custom_prompts_for_user(
        db, user_id=current_user.user_id, content_module=content_module, article_type=article_type
    )
    return prompts

@router.get("/{custom_prompt_id}", response_model=prompt_schemas.UserCustomPromptResponse)
async def read_my_specific_custom_prompt(
    custom_prompt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Obtiene una plantilla de system prompt personalizada específica del usuario actual.
    """
    prompt = prompt_crud.get_user_custom_prompt_by_id(db, custom_prompt_id=custom_prompt_id, user_id=current_user.user_id)
    if prompt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plantilla de prompt personalizada no encontrada.")
    return prompt

@router.put("/{custom_prompt_id}", response_model=prompt_schemas.UserCustomPromptResponse)
async def update_my_custom_prompt(
    custom_prompt_id: uuid.UUID,
    prompt_update_data: prompt_schemas.UserCustomPromptUpdate,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Actualiza una plantilla de system prompt personalizada del usuario actual.
    """
    # Validaciones opcionales si los campos se actualizan
    if prompt_update_data.content_module and prompt_update_data.content_module not in ['linkedin', 'blog']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Módulo de contenido inválido.")
    # ... más validaciones si es necesario ...

    updated_prompt = prompt_crud.update_user_custom_prompt(
        db, custom_prompt_id=custom_prompt_id, user_id=current_user.user_id, prompt_update_data=prompt_update_data
    )
    if updated_prompt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plantilla de prompt personalizada no encontrada para actualizar.")
    return updated_prompt

@router.delete("/{custom_prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_custom_prompt(
    custom_prompt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Elimina una plantilla de system prompt personalizada del usuario actual.
    """
    deleted_prompt = prompt_crud.delete_user_custom_prompt(db, custom_prompt_id=custom_prompt_id, user_id=current_user.user_id)
    if deleted_prompt is None: # O si la función delete retorna False en caso de no encontrar
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plantilla de prompt personalizada no encontrada para eliminar.")
    return None # Respuesta 204