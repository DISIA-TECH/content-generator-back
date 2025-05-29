# NUEVO ARCHIVO

from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from core import models as db_models
from schemas import prompt_schemas

# --- CRUD para SystemPromptTemplate (Globales) ---

def get_system_prompt_templates(
    db: Session, 
    content_module: Optional[str] = None, 
    article_type: Optional[str] = None,
    style_key: Optional[str] = None,
    is_active: bool = True # Por defecto, solo traer activos
) -> List[db_models.SystemPromptTemplate]:
    """
    Obtiene plantillas de system prompt base, opcionalmente filtradas.
    """
    query = db.query(db_models.SystemPromptTemplate)
    if is_active is not None:
        query = query.filter(db_models.SystemPromptTemplate.is_active == is_active)
    if content_module:
        query = query.filter(db_models.SystemPromptTemplate.content_module == content_module)
    if article_type: # Permitir NULL también si article_type es None
        query = query.filter(db_models.SystemPromptTemplate.article_type == article_type)
    elif content_module == 'blog' and article_type is None: # Manejar caso donde article_type no se especifica para blog
        query = query.filter(db_models.SystemPromptTemplate.article_type.is_(None))
    if style_key:
         query = query.filter(db_models.SystemPromptTemplate.style_key == style_key)
        
    return query.order_by(db_models.SystemPromptTemplate.display_name).all()

def get_system_prompt_template_by_id(db: Session, template_id: uuid.UUID) -> Optional[db_models.SystemPromptTemplate]:
    return db.query(db_models.SystemPromptTemplate).filter(db_models.SystemPromptTemplate.template_id == template_id).first()


# --- CRUD para UserCustomPrompt (Específicos del Usuario) ---

def create_user_custom_prompt(
    db: Session, 
    user_id: uuid.UUID, 
    prompt_data: prompt_schemas.UserCustomPromptCreate
) -> db_models.UserCustomPrompt:
    db_prompt = db_models.UserCustomPrompt(
        **prompt_data.model_dump(),
        user_id=user_id
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

def get_user_custom_prompt_by_id(
    db: Session, 
    custom_prompt_id: uuid.UUID, 
    user_id: uuid.UUID
) -> Optional[db_models.UserCustomPrompt]:
    return db.query(db_models.UserCustomPrompt)\
             .filter(db_models.UserCustomPrompt.custom_prompt_id == custom_prompt_id, 
                     db_models.UserCustomPrompt.user_id == user_id)\
             .first()

def get_user_custom_prompts_for_user(
    db: Session, 
    user_id: uuid.UUID, 
    content_module: Optional[str] = None, 
    article_type: Optional[str] = None
) -> List[db_models.UserCustomPrompt]:
    query = db.query(db_models.UserCustomPrompt)\
              .filter(db_models.UserCustomPrompt.user_id == user_id)
    if content_module:
        query = query.filter(db_models.UserCustomPrompt.content_module == content_module)
    if article_type:
        query = query.filter(db_models.UserCustomPrompt.article_type == article_type)
    elif content_module == 'blog' and article_type is None:
         query = query.filter(db_models.UserCustomPrompt.article_type.is_(None))

    return query.order_by(db_models.UserCustomPrompt.prompt_name).all()

def update_user_custom_prompt(
    db: Session, 
    custom_prompt_id: uuid.UUID, 
    user_id: uuid.UUID, 
    prompt_update_data: prompt_schemas.UserCustomPromptUpdate
) -> Optional[db_models.UserCustomPrompt]:
    db_prompt = get_user_custom_prompt_by_id(db, custom_prompt_id, user_id)
    if db_prompt:
        update_data = prompt_update_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(db_prompt, key):
                setattr(db_prompt, key, value)
        db_prompt.updated_at = datetime.now(datetime.timezone.utc)
        db.commit()
        db.refresh(db_prompt)
    return db_prompt

def delete_user_custom_prompt(
    db: Session, 
    custom_prompt_id: uuid.UUID, 
    user_id: uuid.UUID
) -> Optional[db_models.UserCustomPrompt]:
    db_prompt = get_user_custom_prompt_by_id(db, custom_prompt_id, user_id)
    if db_prompt:
        db.delete(db_prompt)
        db.commit()
    return db_prompt # Retorna el objeto eliminado (o None si no se encontró)