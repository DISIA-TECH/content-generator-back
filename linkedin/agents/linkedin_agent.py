# MODIFICADO: Añadir la implementación de generate_content.

from common.base_agent import BaseAgent
from linkedin.models.linkedin_models import LinkedInPostRequestRefactored, LinkedInPostResponseRefactored
from core.logger import get_logger
from core.config import settings 
from typing import Optional, Any # Any añadido para el tipo de retorno de generate_content

logger = get_logger("linkedin_agent")

PABLO_LINKEDIN_SYSTEM_PROMPT_PREFIX = (
    "Eres un asistente que escribe publicaciones de LinkedIn con el estilo y tono de Pablo Pérez, "
    "usando emojis y saltos de línea como él. Es clave que te centres en sus palabras más particulares. "
    "Identifica cuáles son las que marcan su estilo y aplícalas para evitar el tono genérico y formal, "
    "y replicar el propio de Pablo.\n"
    "Importante: Si bien te identificas como Pablo Pérez, OMITE el dato de que "
    "formas parte de la Built Academy. No hables de Built Academy a menos que te lo soliciten "
    "explícitamente en el Human Prompt (HumanMessage)\n\n"
)

AITOR_LINKEDIN_SYSTEM_PROMPT_PREFIX = (
    "Eres un asistente que escribe publicaciones de LinkedIn con el estilo y tono de Aitor Pastor. "
    "Es clave que te centres en sus palabras más particulares. Identifica cuáles son las que marcan su estilo "
    "y aplícalas para evitar el tono genérico y replicar el propio de Aitor.\n\n"
)


class LinkedInAgent(BaseAgent):
    """Agente refactorizado para generación de posts de LinkedIn."""
    
    def __init__(
        self,
        model_identifier: str, 
        temperature: float,
    ):
        actual_model_name = settings.MODEL_MAPPING.get(model_identifier)
        if not actual_model_name:
            error_msg = f"Identificador de modelo '{model_identifier}' no encontrado en MODEL_MAPPING. Disponibles: {list(settings.MODEL_MAPPING.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        super().__init__(
            model_name=actual_model_name, 
            temperature=temperature
        )
        self.model_identifier_key = model_identifier 
        logger.info(f"Agente de LinkedIn inicializado. Frontend model key: '{model_identifier}', LLM model: '{actual_model_name}', Temp: {temperature}")

    # MODIFICADO: Añadir implementación de generate_content
    async def generate_content(self, **kwargs) -> Any:
        """
        Implementación del método abstracto de BaseAgent.
        Delega a generate_post_refactored si 'request' está en kwargs y es del tipo correcto.
        """
        request_data = kwargs.get("request")
        if isinstance(request_data, LinkedInPostRequestRefactored):
            return await self.generate_post_refactored(request_data)
        else:
            logger.error("LinkedInAgent.generate_content llamado sin un 'request' válido de tipo LinkedInPostRequestRefactored.")
            raise NotImplementedError(
                "LinkedInAgent.generate_content espera un argumento 'request' de tipo LinkedInPostRequestRefactored."
            )

    def _apply_author_prefix_to_system_prompt(self, system_prompt: str, model_key: Optional[str] = None) -> str:
        key_to_check = model_key if model_key else self.model_identifier_key
        if key_to_check == "Pablo":
            logger.info("Aplicando prefijo de Pablo para LinkedIn.")
            return PABLO_LINKEDIN_SYSTEM_PROMPT_PREFIX + system_prompt
        elif key_to_check == "Aitor":
            logger.info("Aplicando prefijo de Aitor para LinkedIn.")
            return AITOR_LINKEDIN_SYSTEM_PROMPT_PREFIX + system_prompt
        return system_prompt

    async def generate_post_refactored(self, request: LinkedInPostRequestRefactored) -> LinkedInPostResponseRefactored:
        logger.info(f"Solicitud para generar post de LinkedIn: Tema='{request.human_prompt[:50]}...', Modelo/Estilo='{request.model}', Temp='{request.temperature}'")
        
        effective_system_prompt = self._apply_author_prefix_to_system_prompt(request.system_prompt, request.model)
        
        logger.debug(f"System Prompt final a usar para LinkedIn: '{effective_system_prompt[:200]}...'") 
            
        target_actual_llm_model_name = settings.MODEL_MAPPING.get(request.model)

        if not target_actual_llm_model_name: 
            error_msg = f"Modelo/Estilo '{request.model}' no reconocido en la solicitud. Disponibles: {list(settings.MODEL_MAPPING.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if self.model_name != target_actual_llm_model_name or self.temperature != request.temperature:
            logger.info(f"Actualizando configuración del LLM para esta solicitud LinkedIn: Modelo de '{self.model_name}' a '{target_actual_llm_model_name}', Temperatura de '{self.temperature}' a '{request.temperature}'")
            self.update_llm_config(
                model_name=target_actual_llm_model_name,
                temperature=request.temperature
            )
        
        generated_text = await self._call_llm_with_prompts(
            system_prompt=effective_system_prompt, 
            human_prompt=request.human_prompt
        )
        
        logger.info(f"Post de LinkedIn generado exitosamente para el tema: '{request.human_prompt[:50]}...'")

        return LinkedInPostResponseRefactored(
            generated_post=generated_text,
            model_used=request.model, 
            actual_model_name_used=self.model_name, 
            temperature_used=self.temperature
        )