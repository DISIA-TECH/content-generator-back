# (Nuevo archivo para dependencias comunes, como obtener el usuario actual)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from core.database import get_db
from core.security import decode_access_token
from schemas import token_schemas
from crud import user_crud
from core.config import settings
from core import models as db_models
from typing import Optional


# Define el esquema de autenticación OAuth2
# tokenUrl apunta al endpoint de login donde se obtiene el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> db_models.User:
    """
    Dependencia para obtener el usuario actual a partir del token JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id_str: Optional[str] = payload.get("sub") # Asumimos que el user_id (UUID) está en 'sub'
    if user_id_str is None:
        raise credentials_exception
    
    # token_data = token_schemas.TokenData(user_id=user_id_str) # No es necesario si solo usamos user_id
    
    user = user_crud.get_user_by_id(db, user_id=user_id_str)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: db_models.User = Depends(get_current_user)
) -> db_models.User:
    """
    Dependencia para obtener el usuario actual activo.
    Podrías añadir una comprobación de 'is_active' si tu modelo User la tuviera.
    """
    # if not current_user.is_active: # Si tuvieras un campo is_active en el modelo User
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user