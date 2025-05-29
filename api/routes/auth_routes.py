# MODIFICADO: Se cambian las importaciones de los esquemas.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password
# MODIFICADO: Importaciones más explícitas de los esquemas Pydantic
from schemas.user_schemas import UserCreate, UserResponse
from schemas.token_schemas import Token
from crud import user_crud
# from core.config import settings # No se usa settings directamente aquí

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    created_user = user_crud.create_user(db=db, user=user)
    return created_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends() 
):
    user = user_crud.get_user_by_email(db, email=form_data.username) 
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}