# (Refactorizado para la nueva lógica y modelos)

from typing import Optional, Dict, List, Any # Any añadido para el retorno de generate_content
from common.base_agent import BaseAgent
from blog.models.blog_models import (
    GeneralInterestBlogRequest,
    SuccessCaseBlogRequest,
    BlogArticleResponse,
    SuccessCaseBlogResponse
)
from blog.prompts import blog_prompts 
from common.utils.helpers import extract_text_from_pdf, extract_content_from_url, chunk_text, format_content_for_readability
from core.logger import get_logger
from core.config import settings

logger = get_logger("blog_agent")

PABLO_BLOG_SYSTEM_PROMPT_PREFIX = "Escribe este artículo de blog con el estilo y tono distintivo de Pablo Pérez...\n\n"
AITOR_BLOG_SYSTEM_PROMPT_PREFIX = "Redacta este artículo de blog con el estilo y la perspectiva única de Aitor Pastor...\n\n"


class BlogAgent(BaseAgent):
    """
    Agente refactorizado para la generación de artículos de blog,
    manejando tanto interés general como casos de éxito.
    """

    def __init__(self, model_identifier: str, temperature: float, max_tokens: Optional[int] = None):
        actual_model_name = settings.MODEL_MAPPING.get(model_identifier)
        if not actual_model_name:
            error_msg = f"Modelo/Autor '{model_identifier}' no encontrado en MODEL_MAPPING."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        super().__init__(
            model_name=actual_model_name,
            temperature=temperature,
            max_tokens=max_tokens or settings.DEFAULT_MAX_TOKENS
        )
        self.model_identifier_key = model_identifier 
        logger.info(f"BlogAgent inicializado. Frontend model key: '{model_identifier}', LLM: '{actual_model_name}', Temp: {temperature}")

    # MODIFICADO: Añadir implementación de generate_content
    async def generate_content(self, **kwargs) -> Any:
        """
        Implementación del método abstracto de BaseAgent.
        Este método no está diseñado para ser llamado directamente por el BlogService en su forma actual,
        ya que el servicio llama a métodos más específicos.
        Si se necesitara una llamada genérica, se requeriría lógica para determinar
        el tipo de artículo (ej: GeneralInterest o SuccessCase) a partir de kwargs.
        """
        logger.warning("BlogAgent.generate_content(**kwargs) llamado. Esta ruta no está completamente implementada para despacho genérico.")
        # Ejemplo de cómo podría funcionar un despacho (requeriría pasar un 'request_type' o 'request_object')
        # request_object = kwargs.get("request")
        # if isinstance(request_object, GeneralInterestBlogRequest):
        #     return await self.generate_general_interest_article(request_object)
        # elif isinstance(request_object, SuccessCaseBlogRequest):
        #     pdf_bytes = kwargs.get("pdf_bytes")
        #     return await self.generate_success_case_article(request_object, pdf_bytes)
        raise NotImplementedError(
            "BlogAgent.generate_content no está implementado para uso genérico. "
            "Llame a generate_general_interest_article o generate_success_case_article directamente."
        )

    def _apply_author_prefix_to_system_prompt(self, system_prompt: str) -> str:
        if self.model_identifier_key == "Pablo":
            return PABLO_BLOG_SYSTEM_PROMPT_PREFIX + system_prompt
        elif self.model_identifier_key == "Aitor":
            return AITOR_BLOG_SYSTEM_PROMPT_PREFIX + system_prompt
        return system_prompt

    async def _research_urls(self, topic: str, urls: List[str], web_research_options: Dict[str, Any]) -> Optional[str]:
        if not urls:
            return None

        url_contents = []
        for url_str in urls:
            logger.info(f"Extrayendo contenido de URL para investigación: {url_str}")
            content = extract_content_from_url(str(url_str)) 
            if content:
                chunks = chunk_text(content, chunk_size=3000, chunk_overlap=300) 
                url_contents.extend(chunks) 
            else:
                logger.warning(f"No se pudo extraer contenido de {url_str}")
        
        if not url_contents:
            logger.info("No se extrajo contenido de ninguna URL para investigación.")
            return None

        combined_url_text = "\n\n---\n\n".join(url_contents[:5]) 
        
        web_search_llm = BlogAgent(model_identifier="Default", temperature=0.3) 
        
        research_human_prompt = (
            f"Tema principal: {topic}\n\n"
            f"Contenido extraído de URLs de referencia:\n{combined_url_text}\n\n"
            "Por favor, proporciona un resumen conciso y factual de la información más relevante de este contenido "
            "en relación con el tema principal, para ser usado en un artículo de blog."
        )
        
        logger.info(f"Llamando a LLM de búsqueda web para resumir contenido de URLs. Modelo: {web_search_llm.model_name}")
        try:
            summary = await web_search_llm._call_llm_with_prompts(
                system_prompt=blog_prompts.WEB_RESEARCH_SYSTEM_PROMPT,
                human_prompt=research_human_prompt
            )
            logger.info("Resumen de investigación web obtenido.")
            return summary
        except Exception as e:
            logger.error(f"Error durante la investigación web con LLM: {e}", exc_info=True)
            return "Error al procesar la información de las URLs."


    async def generate_general_interest_article(self, request: GeneralInterestBlogRequest) -> BlogArticleResponse:
        logger.info(f"Iniciando generación de artículo de interés general. Tema: '{request.human_prompt[:50]}...'")

        final_system_prompt = self._apply_author_prefix_to_system_prompt(request.system_prompt)
        current_human_prompt = request.human_prompt
        researched_summary = None

        if request.urls_to_research:
            logger.info(f"Investigando URLs para el tema: {request.human_prompt[:50]}...")
            researched_summary = await self._research_urls(
                request.human_prompt, 
                request.urls_to_research,
                request.web_research_options.model_dump() if request.web_research_options else {}
            )
            if researched_summary:
                current_human_prompt = (
                    f"{request.human_prompt}\n\n"
                    f"--- Resumen de Investigación Adicional ---\n"
                    f"{researched_summary}\n"
                    f"--- Fin del Resumen de Investigación ---"
                )
                logger.info("Resumen de investigación añadido al human_prompt.")

        if self.model_identifier_key != request.model or self.temperature != request.temperature or (request.max_tokens_article and self.max_tokens != request.max_tokens_article) :
            new_model_name = settings.MODEL_MAPPING.get(request.model, self.model_name)
            self.update_llm_config(
                model_name=new_model_name, 
                temperature=request.temperature,
                max_tokens=request.max_tokens_article
            )
        
        article_content = await self._call_llm_with_prompts(
            system_prompt=final_system_prompt,
            human_prompt=current_human_prompt
        )

        return BlogArticleResponse(
            generated_article=format_content_for_readability(article_content),
            model_used=request.model,
            actual_model_name_used=self.model_name,
            temperature_used=self.temperature,
            researched_content_summary=researched_summary
        )

    async def _transform_pdf_text_for_blog(self, pdf_text: str, target_style_prompt: str) -> str:
        if not pdf_text:
            return ""
        
        logger.info(f"Transformando texto de PDF (longitud: {len(pdf_text)}) para estilo blog.")
        
        transformed_text = await self._call_llm_with_prompts(
            system_prompt=blog_prompts.PDF_TRANSFORMATION_SYSTEM_PROMPT,
            human_prompt=pdf_text[:15000] 
        )
        logger.info("Texto de PDF transformado para blog.")
        return transformed_text

    async def _summarize_article(self, article_text: str, max_tokens_summary: Optional[int]) -> str:
        if not article_text:
            return ""

        original_max_tokens = self.max_tokens
        summary_max_tokens = max_tokens_summary or 250 
        self.update_llm_config(max_tokens=summary_max_tokens) 

        logger.info(f"Resumiendo artículo (max_tokens para resumen: {summary_max_tokens}).")
        
        summary_human_prompt = f"Por favor, resume el siguiente artículo de caso de éxito:\n\n{article_text}"
        
        summary = await self._call_llm_with_prompts(
            system_prompt=blog_prompts.SUCCESS_CASE_SUMMARY_SYSTEM_PROMPT,
            human_prompt=summary_human_prompt
        )
        
        self.update_llm_config(max_tokens=original_max_tokens)
        
        logger.info("Resumen de artículo generado.")
        return summary

    async def generate_success_case_article(
        self, request: SuccessCaseBlogRequest, pdf_bytes: Optional[bytes]
    ) -> SuccessCaseBlogResponse:
        logger.info(f"Iniciando generación de caso de éxito. Tema: '{request.human_prompt[:50]}...'")

        final_system_prompt = self._apply_author_prefix_to_system_prompt(request.system_prompt)
        current_human_prompt = request.human_prompt

        if pdf_bytes:
            logger.info("Procesando archivo PDF para caso de éxito.")
            pdf_text = extract_text_from_pdf(pdf_bytes)
            if pdf_text:
                transformed_pdf_text = await self._transform_pdf_text_for_blog(pdf_text, request.system_prompt)
                current_human_prompt = (
                    f"Contexto principal del caso de éxito: {request.human_prompt}\n\n"
                    f"--- Información Relevante del Documento Técnico (reescrita para un blog) ---\n"
                    f"{transformed_pdf_text}\n"
                    f"--- Fin de la Información del Documento ---"
                )
                logger.info("Texto de PDF transformado y añadido al human_prompt.")
            else:
                logger.warning("No se pudo extraer texto del PDF o el PDF estaba vacío.")

        if self.model_identifier_key != request.model or self.temperature != request.temperature or (request.max_tokens_article and self.max_tokens != request.max_tokens_article):
            new_model_name = settings.MODEL_MAPPING.get(request.model, self.model_name)
            self.update_llm_config(
                model_name=new_model_name, 
                temperature=request.temperature,
                max_tokens=request.max_tokens_article
            )

        full_article_content = await self._call_llm_with_prompts(
            system_prompt=final_system_prompt,
            human_prompt=current_human_prompt
        )
        logger.info("Artículo de caso de éxito completo generado.")

        summary_article_content = await self._summarize_article(full_article_content, request.max_tokens_summary)

        return SuccessCaseBlogResponse(
            full_article=format_content_for_readability(full_article_content),
            summary_article=format_content_for_readability(summary_article_content),
            model_used=request.model,
            actual_model_name_used=self.model_name, 
            temperature_used=self.temperature,
        )