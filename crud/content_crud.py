# MODIFICADO: Ajustar funciones y añadir nuevas para el historial

from sqlalchemy.orm import Session
from typing import Optional, List
import uuid 
from datetime import datetime

from core import models as db_models 
from schemas import content_schemas # Usar los esquemas de contenido

def create_generated_content(
    db: Session, 
    user_id: uuid.UUID, 
    content_data: content_schemas.GeneratedContentCreate
) -> db_models.GeneratedContent:
    db_content = db_models.GeneratedContent(
        **content_data.model_dump(exclude_none=True), # Excluir Nones para campos opcionales
        user_id=user_id
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def get_generated_content_by_id_for_user( # Renombrado para claridad
    db: Session, 
    content_id: uuid.UUID, 
    user_id: uuid.UUID
) -> Optional[db_models.GeneratedContent]:
    return db.query(db_models.GeneratedContent)\
             .filter(db_models.GeneratedContent.content_id == content_id, 
                     db_models.GeneratedContent.user_id == user_id,
                     db_models.GeneratedContent.is_deleted == False)\
             .first()

def get_all_generated_content_for_user(
    db: Session, 
    user_id: uuid.UUID, 
    skip: int = 0, 
    limit: int = 20, # Límite por defecto más pequeño para listas
    content_type: Optional[str] = None
    # TODO: Añadir filtros por tags, búsqueda por texto
) -> List[db_models.GeneratedContent]:
    query = db.query(db_models.GeneratedContent)\
              .filter(db_models.GeneratedContent.user_id == user_id,
                      db_models.GeneratedContent.is_deleted == False)
    
    if content_type:
        query = query.filter(db_models.GeneratedContent.content_type == content_type)
        
    return query.order_by(db_models.GeneratedContent.created_at.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()

def update_generated_content( # Función más genérica para actualizar
    db: Session, 
    content_id: uuid.UUID, 
    user_id: uuid.UUID, 
    content_update_data: content_schemas.GeneratedContentUpdate # Usar el nuevo schema
) -> Optional[db_models.GeneratedContent]:
    db_content = get_generated_content_by_id_for_user(db, content_id, user_id)
    if db_content:
        update_data = content_update_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(db_content, key): # Solo actualizar atributos que existen en el modelo
                setattr(db_content, key, value)
        db_content.updated_at = datetime.now(datetime.timezone.utc) 
        db.commit()
        db.refresh(db_content)
    return db_content

def delete_generated_content_logically( # Renombrado para claridad
    db: Session, 
    content_id: uuid.UUID, 
    user_id: uuid.UUID
) -> Optional[db_models.GeneratedContent]:
    db_content = get_generated_content_by_id_for_user(db, content_id, user_id)
    if db_content:
        db_content.is_deleted = True
        db_content.updated_at = datetime.now(datetime.timezone.utc) 
        db.commit()
        db.refresh(db_content)
    return db_content