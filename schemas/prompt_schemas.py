# NUEVO ARCHIVO

from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

# --- System Prompt Template Schemas (Globales) ---
class SystemPromptTemplateBase(BaseModel):
    template_name: str
    content_module: str # 'linkedin' o 'blog'
    article_type: Optional[str] = None # 'general_interest', 'success_case', o None
    style_key: str # 'Default', 'Pablo', 'Technical', etc.
    display_name: str
    prompt_text: str
    is_active: bool = True

class SystemPromptTemplateResponse(SystemPromptTemplateBase):
    template_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- User Custom Prompt Schemas (Específicos del Usuario) ---
class UserCustomPromptBase(BaseModel):
    prompt_name: str = Field(..., min_length=1, max_length=255, description="Nombre dado por el usuario a su plantilla personalizada")
    content_module: str = Field(..., description="Módulo de contenido: 'linkedin' o 'blog'")
    article_type: Optional[str] = Field(None, description="Tipo de artículo para blog: 'general_interest', 'success_case', o None")
    prompt_text: str = Field(..., description="El texto del system prompt personalizado")

class UserCustomPromptCreate(UserCustomPromptBase):
    pass

class UserCustomPromptUpdate(BaseModel):
    prompt_name: Optional[str] = Field(None, min_length=1, max_length=255)
    content_module: Optional[str] = None # Generalmente no se cambia, pero podría ser
    article_type: Optional[str] = None
    prompt_text: Optional[str] = None

class UserCustomPromptResponse(UserCustomPromptBase):
    custom_prompt_id: uuid.UUID
    user_id: uuid.UUID # Podría omitirse en la respuesta si siempre es el del usuario actual
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True