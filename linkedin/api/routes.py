# MODIFICADO: Para pasar db session y current_user al servicio

from fastapi import APIRouter, Depends, HTTPException, status, Body 
from sqlalchemy.orm import Session # Importar Session
import uuid # Para el tipo UUID

from linkedin.models.linkedin_models import (
    LinkedInPostRequestRefactored,  
    LinkedInPostResponseRefactored  
)
from linkedin.services.linkedin_service import LinkedInService 
from core.logger import get_logger
from core.database import get_db # Importar get_db
from api.dependencies import get_current_active_user # Importar dependencia de usuario
from core import models as db_models # Para el tipo de current_user

logger = get_logger("linkedin_api_routes") 

router = APIRouter(prefix="/linkedin", tags=["LinkedIn Refactored"])

def get_linkedin_service() -> LinkedInService:
    return LinkedInService() 

@router.post("/generate_post_refactored", response_model=LinkedInPostResponseRefactored) 
async def generate_linkedin_post_refactored_endpoint(
    request: LinkedInPostRequestRefactored = Body(...), 
    service: LinkedInService = Depends(get_linkedin_service),
    db: Session = Depends(get_db), # Añadir dependencia de BD
    current_user: db_models.User = Depends(get_current_active_user) # Añadir dependencia de usuario actual
):
    try:
        logger.info(f"API LinkedIn: Recibida solicitud de {current_user.email} para generar post: {request.model_dump_json(indent=2)}")
        # Pasar db y user_id al método del servicio
        return await service.generate_post_service_method(request=request, db=db, user_id=current_user.user_id)
    except ValueError as ve: 
        logger.warning(f"API LinkedIn: Error de validación/configuración: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"API LinkedIn: Error interno al generar post: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor al generar el post: {str(e)}"
        )