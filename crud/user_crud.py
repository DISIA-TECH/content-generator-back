# (Se añade import de datetime para UserPreferenceResponse)
from sqlalchemy.orm import Session
from typing import Optional
from core import models as db_models 
from schemas import user_schemas 
from core.security import get_password_hash, verify_password
from datetime import datetime # Importar datetime
import uuid

def get_user_by_id(db: Session, user_id: str) -> Optional[db_models.User]:
    return db.query(db_models.User).filter(db_models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[db_models.User]:
    return db.query(db_models.User).filter(db_models.User.email == email).first()

def create_user(db: Session, user: user_schemas.UserCreate) -> db_models.User:
    hashed_password = get_password_hash(user.password)
    db_user = db_models.User(
        email=user.email, 
        hashed_password=hashed_password, 
        preferred_name=user.preferred_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Crear preferencias por defecto para el nuevo usuario
    # Asegurarse de que user_id se pasa como UUID si el modelo lo espera, o string si el CRUD lo maneja.
    # El modelo UserPreference tiene user_id como PG_UUID(as_uuid=True)
    create_user_preferences(db, user_id=db_user.user_id, preferences_data=user_schemas.UserPreferenceCreate())
    return db_user

def update_user(db: Session, user_id: uuid.UUID, user_update: user_schemas.UserUpdate) -> Optional[db_models.User]:
    db_user = get_user_by_id(db, str(user_id)) # Convertir UUID a string para la búsqueda si get_user_by_id espera str
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db_user.updated_at = datetime.now(datetime.timezone.utc) # Actualizar manualmente si onupdate no funciona como esperado
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_preferences(db: Session, user_id: uuid.UUID) -> Optional[db_models.UserPreference]:
    return db.query(db_models.UserPreference).filter(db_models.UserPreference.user_id == user_id).first()

def create_user_preferences(db: Session, user_id: uuid.UUID, preferences_data: user_schemas.UserPreferenceCreate) -> db_models.UserPreference:
    db_preferences = get_user_preferences(db, user_id)
    if db_preferences: 
        update_data = preferences_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_preferences, key, value)
        db_preferences.updated_at = datetime.now(datetime.timezone.utc)
    else: 
        db_preferences = db_models.UserPreference(**preferences_data.model_dump(), user_id=user_id)
        db.add(db_preferences)
    
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

def update_user_preferences(db: Session, user_id: uuid.UUID, preferences_update: user_schemas.UserPreferenceUpdate) -> Optional[db_models.UserPreference]:
    return create_user_preferences(db, user_id, preferences_update)