# MODIFICADO: Asegurar que urls_researched se pase como lista de strings
from sqlalchemy.orm import Session 
import uuid 
from typing import Optional, Dict, Any, List 
from pydantic import HttpUrl 

from blog.agents.blog_agent import BlogAgent 
from blog.models.blog_models import (
    GeneralInterestBlogRequest,
    SuccessCaseBlogRequest,
    BlogArticleResponse,
    SuccessCaseBlogResponse,
    BlogPromptCustomizationRequest 
)
from core.logger import get_logger
from crud import content_crud 
from schemas.content_schemas import GeneratedContentCreate 
from core.config import settings 

logger = get_logger("blog_service")

class BlogService:
    def __init__(self):
        logger.info("BlogService inicializado.")
    
    async def generate_general_interest_article(
        self, 
        request: GeneralInterestBlogRequest,
        db: Session, 
        user_id: uuid.UUID 
    ) -> BlogArticleResponse:
        logger.info(f"Servicio Blog: Solicitud interés general. Tema: '{request.human_prompt[:50]}...' Usuario: {user_id}")
        try:
            agent = BlogAgent(
                model_identifier=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens_article
            )
            article_response = await agent.generate_general_interest_article(request)

            urls_researched_as_strings: Optional[List[str]] = None
            if request.urls_to_research:
                urls_researched_as_strings = [str(url) for url in request.urls_to_research]

            content_to_save = GeneratedContentCreate(
                content_type='blog_general_interest',
                custom_title=request.human_prompt[:100], 
                human_prompt_used=request.human_prompt,
                system_prompt_used=agent._apply_author_prefix_to_system_prompt(request.system_prompt),
                model_key_selected=request.model,
                actual_llm_model_name_used=agent.model_name,
                temperature_used=agent.temperature,
                max_tokens_article_used=request.max_tokens_article,
                urls_researched=urls_researched_as_strings, 
                web_research_options_used=request.web_research_options.model_dump() if request.web_research_options else None,
                generated_text_main=article_response.generated_article,
                researched_content_summary=article_response.researched_content_summary
            )
            content_crud.create_generated_content(db=db, user_id=user_id, content_data=content_to_save)
            logger.info(f"Artículo de interés general guardado en historial para usuario {user_id}")
            
            return article_response 
        except Exception as e:
            logger.error(f"Error en BlogService (interés general): {str(e)}", exc_info=True)
            raise

    async def generate_success_case_article(
        self, 
        request: SuccessCaseBlogRequest, 
        db: Session, 
        user_id: uuid.UUID, 
        pdf_bytes: Optional[bytes] = None,
        pdf_filename: Optional[str] = None # Añadir filename para el historial
    ) -> SuccessCaseBlogResponse:
        logger.info(f"Servicio Blog: Solicitud caso de éxito. Tema: '{request.human_prompt[:50]}...' Usuario: {user_id}")
        try:
            agent = BlogAgent(
                model_identifier=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens_article 
            )
            case_response = await agent.generate_success_case_article(request, pdf_bytes)

            content_to_save = GeneratedContentCreate(
                content_type='blog_success_case',
                custom_title=request.human_prompt[:100],
                human_prompt_used=request.human_prompt, 
                system_prompt_used=agent._apply_author_prefix_to_system_prompt(request.system_prompt),
                model_key_selected=request.model,
                actual_llm_model_name_used=agent.model_name,
                temperature_used=agent.temperature,
                max_tokens_article_used=request.max_tokens_article,
                max_tokens_summary_used=request.max_tokens_summary,
                pdf_filename_original= pdf_filename, # Usar el filename pasado
                generated_text_main=case_response.full_article,
                generated_text_summary=case_response.summary_article
            )
            content_crud.create_generated_content(db=db, user_id=user_id, content_data=content_to_save)
            logger.info(f"Caso de éxito guardado en historial para usuario {user_id}")

            return case_response 
        except Exception as e:
            logger.error(f"Error en BlogService (caso de éxito): {str(e)}", exc_info=True)
            raise
    
    async def get_prompt_configurations(self) -> Dict[str, Any]:
        logger.warning("get_prompt_configurations no está completamente implementado con la nueva estructura de prompts.")
        return {
            "general_interest_default_prompt": "Placeholder para el prompt base de interés general.",
            "success_case_default_prompt": "Placeholder para el prompt base de caso de éxito."
        }

    async def customize_blog_prompt(self, article_type_key: str, request: BlogPromptCustomizationRequest) -> Dict[str, Any]:
        logger.warning(f"customize_blog_prompt para '{article_type_key}' no está completamente implementado.")
        return {"success": False, "message": "Funcionalidad de personalización de prompt base no implementada completamente."}

    async def customize_general_interest_prompt(self, request: BlogPromptCustomizationRequest) -> Dict[str, Any]:
        return await self.customize_blog_prompt("general_interest_default", request)

    async def customize_success_case_prompt(self, request: BlogPromptCustomizationRequest) -> Dict[str, Any]:
        return await self.customize_blog_prompt("success_case_default", request)