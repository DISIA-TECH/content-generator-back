# --- backend/linkedin/models/linkedin_models.py ---
# (Refactorizado para usar los campos directos: human_prompt, model, system_prompt, temperature)

from typing import Literal, List # List es para el response
from pydantic import BaseModel, Field
from core.config import settings
# from common.models.base_models import ContentRequestBase, ContentResponseBase # Usaremos nuestros propios modelos aquí

# Ya no se necesita LinkedInPostStyle ni LinkedInAuthor si el front envía el "model" y el "system_prompt" directamente.
# class LinkedInPostStyle(str, Enum): ...
# class LinkedInAuthor(str, Enum): ...

class LinkedInPostRequestRefactored(BaseModel):
    """
    Modelo de solicitud refactorizado para generar un post de LinkedIn.
    Directamente usa los campos que definimos: human_prompt, model, system_prompt, temperature.
    """
    human_prompt: str = Field(
        ..., # ... indica que es un campo requerido
        description="Instrucción humana o tema para el post. Proviene del campo 'Tema' del frontend.",
        examples=["Novedades sobre IA en marketing digital y su impacto en PYMEs."]
    )
    model: Literal["Default", "Pablo", "Aitor"] = Field(
        ...,
        description="Estilo/modelo a utilizar. Proviene del select box 'Estilo' del frontend. Mapea a un modelo LLM específico.",
        examples=["Default"]
    )
    system_prompt: str = Field(
        ...,
        description="Prompt del sistema, editable por el usuario. Proviene del campo 'Editar Prompt' del frontend.",
        examples=["Eres un experto en crear contenido de liderazgo de pensamiento (Thought Leadership) para LinkedIn..."]
    )
    temperature: float = Field(
        default=settings.DEFAULT_TEMPERATURE, # Tomado de la configuración global
        ge=0.0,
        le=1.0, # Ajustar si tu modelo permite más (e.g. Langchain hasta 2.0)
        description="Temperatura para la generación del contenido (0.0 a 1.0). Proviene del campo 'Temperatura' del frontend.",
        examples=[0.5]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "human_prompt": "El futuro del trabajo remoto y cómo las empresas pueden adaptarse.",
                "model": "Pablo",
                "system_prompt": "Actúa como un futurista del trabajo y consultor de RRHH. Tu objetivo es generar un post de LinkedIn que sea provocador y ofrezca soluciones prácticas. Estructura: 1. Gancho. 2. Problema actual. 3. Soluciones (bullet points). 4. Pregunta para la audiencia.",
                "temperature": 0.6
            }
        }

class LinkedInPostResponseRefactored(BaseModel):
    """Modelo de respuesta refactorizado para un post de LinkedIn generado."""
    generated_post: str = Field(description="El contenido del post de LinkedIn generado.")
    model_used: str = Field(description="El identificador del modelo que se utilizó (e.g., 'Default', 'Pablo', 'Aitor').")
    actual_model_name_used: str = Field(description="El nombre/ID real del modelo LLM que se invocó.")
    temperature_used: float = Field(description="La temperatura que se utilizó para la generación.")
    # hashtags: List[str] = Field(default_factory=list, description="Hashtags sugeridos (opcional, podría añadirse post-procesamiento)")

    class Config:
        json_schema_extra = {
            "example": {
                "generated_post": "El trabajo remoto llegó para quedarse, pero ¿están las empresas realmente preparadas? ... #futurodeltrabajo #trabajoremoto",
                "model_used": "Pablo",
                "actual_model_name_used": "ft:gpt-3.5-turbo:my-org:pablo-model:xxxxxxx",
                "temperature_used": 0.6
            }
        }

# Los modelos LinkedInSystemPromptConfig, LinkedInPostRequest (antiguo), LinkedInPostResponse (antiguo)
# y LinkedInStyleConfigRequest pueden ser eliminados o archivados si ya no se usan.
# Por ahora, los dejo comentados para referencia.
# class LinkedInSystemPromptConfig(SystemPromptConfig): ...
# class LinkedInPostRequest(ContentRequest): ... (Este es el modelo antiguo que tenía muchos campos)
# class LinkedInPostResponse(ContentResponse): ... (Este es el modelo antiguo)
# class LinkedInStyleConfigRequest(BaseModel): ...
# class AuthorModelInfo(BaseModel): ... (Si la info del modelo se maneja solo en config)


# --- backend/common/prompt_templates/base_templates.py ---
# (Este archivo podría ya no ser necesario si los prompts vienen completos del frontend)
# Si decides mantenerlo para el BlogAgent, asegúrate de que no interfiera con la lógica simplificada de LinkedIn.
# Por ahora, lo dejo como estaba, pero LinkedInAgent ya no lo usará directamente.