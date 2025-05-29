# MODIFICADO: Pasar pdf_filename al servicio de caso de éxito
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, status, Form
from typing import Dict, Any, Optional
import json 
from pydantic import ValidationError 
from sqlalchemy.orm import Session 
import uuid 

from blog.models.blog_models import (
    GeneralInterestBlogRequest,
    SuccessCaseBlogRequest,
    BlogArticleResponse,
    SuccessCaseBlogResponse,
    BlogPromptCustomizationRequest 
)
from blog.services.blog_service import BlogService
from core.logger import get_logger
from core.database import get_db 
from api.dependencies import get_current_active_user 
from core import models as db_models 

logger = get_logger("blog_api_routes") 

router = APIRouter(prefix="/blog", tags=["Blog Refactored"])

def get_blog_service() -> BlogService:
    return BlogService()

@router.get("/prompt_config", response_model=Dict[str, Any])
async def get_base_prompt_configurations_endpoint(
    service: BlogService = Depends(get_blog_service)
):
    try:
        return await service.get_prompt_configurations()
    except Exception as e:
        logger.error(f"Error al obtener configuraciones de prompts base: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/prompt_config/general_interest", response_model=Dict[str, Any])
async def customize_general_interest_base_prompt_endpoint(
    request: BlogPromptCustomizationRequest,
    service: BlogService = Depends(get_blog_service)
):
    try:
        return await service.customize_general_interest_prompt(request)
    except Exception as e:
        logger.error(f"Error al personalizar prompt base de interés general: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/prompt_config/success_case", response_model=Dict[str, Any])
async def customize_success_case_base_prompt_endpoint(
    request: BlogPromptCustomizationRequest,
    service: BlogService = Depends(get_blog_service)
):
    try:
        return await service.customize_success_case_prompt(request)
    except Exception as e:
        logger.error(f"Error al personalizar prompt base de caso de éxito: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/generate/general_interest", response_model=BlogArticleResponse)
async def generate_general_interest_article_endpoint(
    request: GeneralInterestBlogRequest, 
    service: BlogService = Depends(get_blog_service),
    db: Session = Depends(get_db), 
    current_user: db_models.User = Depends(get_current_active_user) 
):
    try:
        logger.info(f"API Blog: Solicitud interés general de {current_user.email}. Tema: {request.human_prompt[:50]}...")
        return await service.generate_general_interest_article(request=request, db=db, user_id=current_user.user_id)
    except ValueError as ve: 
        logger.warning(f"API Blog: Error de validación/configuración en interés general: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"API Blog: Error interno al generar artículo de interés general: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/generate/success_case", response_model=SuccessCaseBlogResponse)
async def generate_success_case_article_endpoint(
    request_data_str: str = Form(..., alias="request_data", description="JSON string de SuccessCaseBlogRequest"),
    pdf_file: Optional[UploadFile] = File(None, description="Archivo PDF opcional para el caso de éxito."),
    service: BlogService = Depends(get_blog_service),
    db: Session = Depends(get_db), 
    current_user: db_models.User = Depends(get_current_active_user) 
):
    try:
        try:
            request_dict = json.loads(request_data_str)
            request = SuccessCaseBlogRequest(**request_dict)
        except json.JSONDecodeError:
            logger.warning(f"API Blog: Error decodificando JSON para caso de éxito: {request_data_str[:100]}...")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo 'request_data' no es un JSON válido.")
        except ValidationError as ve:
            logger.warning(f"API Blog: Error de validación Pydantic para caso de éxito: {ve.errors()}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors())

        pdf_filename = pdf_file.filename if pdf_file else None
        logger.info(f"API Blog: Solicitud caso de éxito de {current_user.email}. Tema: {request.human_prompt[:50]}..., PDF: {pdf_filename}")
        
        pdf_bytes: Optional[bytes] = None
        if pdf_file:
            pdf_bytes = await pdf_file.read()
            await pdf_file.close() 

        return await service.generate_success_case_article(
            request=request, 
            db=db, 
            user_id=current_user.user_id, 
            pdf_bytes=pdf_bytes,
            pdf_filename=pdf_filename # Pasar el nombre del archivo al servicio
        )
    except HTTPException: 
        raise
    except Exception as e:
        logger.error(f"API Blog: Error interno al generar caso de éxito: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))