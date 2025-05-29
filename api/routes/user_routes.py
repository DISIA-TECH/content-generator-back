# (Modificado para asegurar que user_id (UUID) se pase como string si es necesario)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core import models as db_models 
from schemas.user_schemas import UserResponse, UserUpdate, UserPreferenceResponse, UserPreferenceUpdate
from crud import user_crud
from api.dependencies import get_current_active_user 
import uuid # Importar uuid

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: db_models.User = Depends(get_current_active_user)
):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_users_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    if user_update.email and user_update.email != current_user.email:
        existing_user = user_crud.get_user_by_email(db, email=user_update.email)
        if existing_user and existing_user.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another user.")

    # user_crud.update_user espera un user_id tipo UUID si el modelo DB lo tiene así.
    # current_user.user_id ya es UUID.
    updated_user = user_crud.update_user(db, user_id=current_user.user_id, user_update=user_update)
    if not updated_user: 
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found during update.")
    return updated_user


@router.get("/me/preferences", response_model=UserPreferenceResponse)
async def read_my_preferences(
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    preferences = user_crud.get_user_preferences(db, user_id=current_user.user_id)
    if not preferences: 
        preferences = user_crud.create_user_preferences(db, user_id=current_user.user_id, preferences_data=UserPreferenceUpdate())
    return preferences

@router.put("/me/preferences", response_model=UserPreferenceResponse)
async def update_my_preferences(
    preferences_update: UserPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user)
):
    updated_preferences = user_crud.update_user_preferences(db, user_id=current_user.user_id, preferences_update=preferences_update)
    return updated_preferences