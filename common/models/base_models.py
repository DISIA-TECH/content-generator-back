# MODIFICADO: Se reintroducen ContentRequest, ContentResponse y SystemPromptConfig
# para compatibilidad con el módulo de blog.

from typing import Dict, Any, Optional, List # List añadido para ContentResponse
from pydantic import BaseModel, Field
from core.config import settings

class ContentRequestBase(BaseModel): 
    """
    Solicitud base simplificada para generación de contenido, usada internamente o para nueva lógica.
    """
    temperature: float = Field(
        default=settings.DEFAULT_TEMPERATURE, 
        ge=0.0, 
        le=1.0, 
        description="Temperatura para la generación del contenido (creatividad)."
    )
    model: Optional[str] = Field(default=None, description="Modelo de lenguaje a utilizar.") # Añadido para coherencia
    max_tokens: Optional[int] = Field(default=settings.DEFAULT_MAX_TOKENS, description="Número máximo de tokens.") # Añadido para coherencia


class ContentResponseBase(BaseModel): 
    """Respuesta base simplificada de generación de contenido, usada internamente o para nueva lógica."""
    generated_content: str # Renombrado desde 'content' para evitar colisión con ContentResponse original
    model_used: str
    temperature_used: float
    # metadata: Dict[str, Any] = Field(default_factory=dict) 


# --- Definiciones para compatibilidad con el módulo de Blog ---
# Estas son las clases que blog/models/blog_models.py espera.
# Se definen de forma simple para resolver el ImportError.
# Si el módulo de blog necesita campos específicos en ellas, estas definiciones
# deberán expandirse o el módulo de blog deberá ser refactorizado.

class SystemPromptConfig(BaseModel):
    """Configuración del system prompt (definición básica para compatibilidad)."""
    role_description: str = "Default role description"
    content_objective: str = "Default content objective"
    style_guidance: str = "Default style guidance"
    structure_description: str = "Default structure description"
    tone: Optional[str] = None
    format_guide: Optional[str] = None
    seo_guidelines: Optional[str] = None
    limitations: Optional[str] = None
    additional_instructions: Optional[str] = None

class ContentRequest(BaseModel):
    """Solicitud base para generación de contenido (definición para compatibilidad)."""
    temperature: Optional[float] = Field(default=settings.DEFAULT_TEMPERATURE, ge=0.0, le=1.0)
    model: Optional[str] = None
    max_tokens: Optional[int] = Field(default=settings.DEFAULT_MAX_TOKENS, description="Número máximo de tokens en la respuesta")
    # system_components: Optional[Dict[str, str]] = None # Este campo estaba en tu original, lo añado por si blog lo usa.
    # Si blog/models/blog_models.py usa campos específicos de aquí, deben estar presentes.
    # Por ejemplo, si blog_models.py espera un campo 'tema' o 'human_prompt', debería añadirse aquí o
    # ContentRequest debería heredar de un modelo que lo tenga.
    # Por ahora, se mantiene simple para resolver el ImportError.
    # Para el error específico "cannot import name 'ContentRequest' from 'common.models.base_models'",
    # solo se necesita que el nombre exista.

class ContentResponse(BaseModel):
    """Respuesta base de generación de contenido (definición para compatibilidad)."""
    content: str # Este era el nombre original del campo
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Si blog_models.py espera otros campos aquí, deben añadirse.

# Los modelos PromptComponent, AgentConfig, HumanPromptConfig
# pueden ser eliminados si ya no se utilizan debido a la simplificación de prompts.
# class PromptComponent(BaseModel): ...
# class AgentConfig(BaseModel): ...
# class HumanPromptConfig(BaseModel): ...