# (Nuevo archivo para esquemas Pydantic relacionados con usuarios y preferencias)

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid # Para el tipo UUID en Pydantic
from datetime import datetime

# --- Esquemas para Usuarios ---
class UserBase(BaseModel):
    email: EmailStr
    preferred_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel): # Para actualizar el perfil
    email: Optional[EmailStr] = None
    preferred_name: Optional[str] = None
    # No permitir actualizar la contraseña directamente aquí, usar un endpoint separado si es necesario

class UserResponse(UserBase):
    user_id: uuid.UUID
    # No incluir hashed_password en las respuestas

    class Config:
        from_attributes = True # Para Pydantic V2 (era orm_mode = True en V1)

# --- Esquemas para Preferencias de Usuario ---
class UserPreferenceBase(BaseModel):
    modelo_linkedin_default: Optional[str] = 'Default'
    temperatura_default_linkedin: Optional[float] = 0.7
    modelo_blog_default: Optional[str] = 'Default'
    temperatura_default_blog: Optional[float] = 0.7

class UserPreferenceCreate(UserPreferenceBase):
    pass # user_id se asignará internamente

class UserPreferenceUpdate(UserPreferenceBase):
    pass

class UserPreferenceResponse(UserPreferenceBase):
    preference_id: uuid.UUID
    user_id: uuid.UUID
    updated_at: datetime

    class Config:
        from_attributes = True