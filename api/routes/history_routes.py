# NUEVO ARCHIVO para los endpoints del historial de contenido

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from core.database import get_db
from core import models as db_models
from schemas import content_schemas # Usar los esquemas de contenido
from crud import content_crud
from api.dependencies import get_current_active_user

router = APIRouter(prefix="/me/history", tags=["Content History"])

@router.get("/", response_model=List[content_schemas.GeneratedContentListItemResponse])
async def read_my_generated_content_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None, description="Filtrar por tipo de contenido (e.g., 'linkedin_post', 'blog_general_interest')"),
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Obtiene el historial de contenido generado para el usuario actual, con paginación y filtros.
    """
    history_items_db = content_crud.get_all_generated_content_for_user(
        db, user_id=current_user.user_id, skip=skip, limit=limit, content_type=content_type
    )
    # Mapear a GeneratedContentListItemResponse, incluyendo snippets
    response_items = []
    for item in history_items_db:
        response_items.append(
            content_schemas.GeneratedContentListItemResponse(
                content_id=item.content_id,
                content_type=item.content_type,
                custom_title=item.custom_title,
                human_prompt_snippet=item.human_prompt_used[:150] + "..." if item.human_prompt_used and len(item.human_prompt_used) > 150 else item.human_prompt_used,
                generated_text_main_snippet=item.generated_text_main[:200] + "..." if item.generated_text_main and len(item.generated_text_main) > 200 else item.generated_text_main,
                model_key_selected=item.model_key_selected,
                created_at=item.created_at,
                updated_at=item.updated_at
                # tags se añadirán después
            )
        )
    return response_items

@router.get("/{content_id}", response_model=content_schemas.GeneratedContentResponse)
async def read_specific_generated_content(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Obtiene un ítem específico del historial de contenido generado por el usuario actual.
    """
    db_content = content_crud.get_generated_content_by_id_for_user(
        db, content_id=content_id, user_id=current_user.user_id
    )
    if db_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contenido no encontrado o no pertenece al usuario.")
    return db_content

@router.put("/{content_id}", response_model=content_schemas.GeneratedContentResponse)
async def update_my_generated_content_item(
    content_id: uuid.UUID,
    content_update: content_schemas.GeneratedContentUpdate,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Actualiza un ítem específico en el historial de contenido del usuario (ej. el título personalizado).
    """
    updated_content = content_crud.update_generated_content(
        db, content_id=content_id, user_id=current_user.user_id, content_update_data=content_update
    )
    if updated_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contenido no encontrado o no se pudo actualizar.")
    return updated_content

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_generated_content_item(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Elimina (borrado lógico) un ítem específico del historial de contenido del usuario.
    """
    deleted_content = content_crud.delete_generated_content_logically(
        db, content_id=content_id, user_id=current_user.user_id
    )
    if deleted_content is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contenido no encontrado o ya eliminado.")
    return None # Respuesta 204 No Content