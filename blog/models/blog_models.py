# (Refactorizado para la nueva estructura de inputs)

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl
from core.config import settings
# Ya no se importa ContentRequest, ContentResponse de base_models para los requests principales del blog
# Se usarán modelos más específicos.

# Opciones para la búsqueda web
class WebResearchOptions(BaseModel):
    search_context_size: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Context size for web research (low, medium, high)."
    )

# --- Modelos de Solicitud Refactorizados ---
class BlogArticleBaseRequest(BaseModel):
    """Modelo base para solicitudes de artículos de blog, con campos comunes."""
    human_prompt: str = Field(..., description="Tema principal o idea central del artículo.")
    model: Literal["Default", "Pablo", "Aitor"] = Field(
        ..., 
        description="Modelo/Autor a utilizar para la generación principal del artículo."
    )
    system_prompt: str = Field(
        ..., 
        description="Prompt del sistema que define el rol, objetivo, estructura, etc., para el artículo final."
    )
    temperature: float = Field(
        default=settings.DEFAULT_TEMPERATURE, 
        ge=0.0, le=1.0, 
        description="Temperatura para la generación del contenido (0.0 a 1.0)."
    )
    max_tokens_article: Optional[int] = Field(
        default=settings.DEFAULT_MAX_TOKENS, # Usar un default general
        description="Máximo de tokens para el artículo principal."
    )

class GeneralInterestBlogRequest(BlogArticleBaseRequest):
    """Solicitud para generar un artículo de blog de interés general."""
    urls_to_research: Optional[List[HttpUrl]] = Field(
        default=None, 
        description="Lista opcional de URLs para investigar y ampliar el tema."
    )
    # model_web: Optional[str] = Field( # Se tomará de settings.MODEL_WEB_SEARCH
    #     default=None, 
    #     description="Modelo a utilizar para la búsqueda web (ej: gpt-4o-search-preview)."
    # )
    web_research_options: Optional[WebResearchOptions] = Field(
        default_factory=WebResearchOptions, # Usa los defaults de WebResearchOptions
        description="Opciones para la búsqueda web, como el tamaño del contexto."
    )
    # Otros campos que eran específicos de GeneralInterestRequest (palabras_clave, longitud, etc.)
    # ahora se espera que se integren en el human_prompt o system_prompt si son necesarios.
    # Si se quieren mantener como campos separados, se pueden añadir aquí.
    # Por simplicidad, se asume que el human_prompt es más libre.

    class Config:
        json_schema_extra = {
            "example": {
                "human_prompt": "El futuro de la inteligencia artificial en la educación primaria y cómo preparará a los niños para los trabajos del mañana. Incluir pros y contras.",
                "model": "Default",
                "system_prompt": "Eres un pedagogo experto en tecnología educativa. Escribe un artículo de blog informativo y atractivo para padres y educadores. Estructura: Introducción, Impacto de la IA, Beneficios, Desafíos, Preparando a los Niños, Conclusión. Tono: Esperanzador pero realista.",
                "temperature": 0.7,
                "urls_to_research": ["https://www.ejemplo.com/ia-educacion-noticia1"],
                "web_research_options": {"search_context_size": "medium"}
            }
        }

class SuccessCaseBlogRequest(BlogArticleBaseRequest):
    """Solicitud para generar un artículo de blog de caso de éxito."""
    # El campo para el PDF se manejará como un UploadFile en el endpoint, no directamente en este modelo Pydantic.
    # El human_prompt puede contener el tema o contexto del caso de éxito.
    # El system_prompt definirá cómo se debe escribir el caso de éxito.
    max_tokens_summary: Optional[int] = Field(
        default=250, # Un default razonable para un resumen
        description="Máximo de tokens para el resumen del caso de éxito."
    )
    class Config:
        json_schema_extra = {
            "example": {
                "human_prompt": "Caso de éxito: Implementación de nuestra solución X en la empresa Y, resultando en un aumento del Z% en eficiencia.",
                "model": "Default",
                "system_prompt": "Eres un redactor de marketing especializado en casos de éxito. Transforma la información técnica proporcionada en un artículo de blog convincente. Estructura: Desafío, Solución, Resultados, Testimonio (si aplica), Conclusión. Tono: Profesional y enfocado en beneficios.",
                "temperature": 0.6,
                "max_tokens_summary": 300
            }
        }

# --- Modelos de Respuesta Refactorizados ---
class BlogArticleResponse(BaseModel):
    """Respuesta para un artículo de blog generado (interés general)."""
    generated_article: str
    model_used: str # El 'model' key ("Default", "Pablo", "Aitor")
    actual_model_name_used: str # El ID real del LLM
    temperature_used: float
    researched_content_summary: Optional[str] = None # Resumen de la investigación web, si se hizo

class SuccessCaseBlogResponse(BaseModel):
    """Respuesta para un artículo de caso de éxito generado."""
    full_article: str
    summary_article: str
    model_used: str
    actual_model_name_used: str
    temperature_used: float
    # pdf_processed_text: Optional[str] = None # Opcional: texto extraído/transformado del PDF

# Modelo para la personalización de prompts (si se mantiene esta funcionalidad)
# Podría simplificarse o eliminarse si el frontend maneja toda la edición del system_prompt.
class BlogPromptCustomizationRequest(BaseModel):
    """Solicitud para personalizar los prompts base del generador de blog (si se usa)."""
    article_type: Literal["general_interest_default", "success_case_default"] # Para saber qué prompt base se actualiza
    # Campos del SystemPromptConfig que se quieren actualizar
    role_description: Optional[str] = None
    content_objective: Optional[str] = None
    style_guidance: Optional[str] = None
    structure_description: Optional[str] = None
    tone: Optional[str] = None
    format_guide: Optional[str] = None
    seo_guidelines: Optional[str] = None
    limitations: Optional[str] = None
    additional_instructions: Optional[str] = None