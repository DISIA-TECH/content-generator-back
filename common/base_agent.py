from abc import ABC, abstractmethod
from typing import Any, List, Optional # Dict ya no es necesario para _get_messages
# import json # No es necesario para logging simplificado aquí

from langchain_core.messages import SystemMessage, HumanMessage # Actualizado
from langchain_openai import ChatOpenAI

# from common.prompt_templates.base_templates import BasePromptTemplate # Ya no es un argumento obligatorio
from core.logger import get_logger
from core.config import settings

logger = get_logger("base_agent")

class BaseAgent(ABC):
    """Clase base refactorizada para agentes de generación de contenido."""
    
    def __init__(
        self,
        # prompt_template: Optional[BasePromptTemplate] = None, # Ya no es el principal motor
        model_name: str, # El nombre/ID real del modelo LLM
        temperature: float,
        max_tokens: int = settings.DEFAULT_MAX_TOKENS # Puede ser útil
    ):
        """
        Inicializa el agente.
        
        Args:
            model_name: Nombre/ID del modelo de lenguaje a utilizar (e.g., "gpt-4o", "ft:...")
            temperature: Temperatura para la generación (creatividad)
            max_tokens: Número máximo de tokens en la respuesta
        """
        # self.prompt_template = prompt_template # Se elimina dependencia directa
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self) -> ChatOpenAI:
        """Inicializa el modelo de lenguaje."""
        logger.info(f"Inicializando LLM con modelo: {self.model_name}, temperatura: {self.temperature}, max_tokens: {self.max_tokens}")
        if not settings.OPENAI_API_KEY:
            logger.error("API Key de OpenAI no configurada en settings.")
            raise ValueError("API Key de OpenAI no configurada.")
        return ChatOpenAI(
            model=self.model_name, # Usar model_name directamente
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=settings.OPENAI_API_KEY
        )
    
    # update_prompt_template ya no es relevante si el system_prompt viene del request
    # def update_prompt_template(self, new_template: BasePromptTemplate) -> None: ...

    def update_llm_config(
        self, 
        model_name: Optional[str] = None, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> None:
        """Actualiza la configuración del LLM y lo reinicializa."""
        if model_name:
            self.model_name = model_name
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens
            
        self.llm = self._initialize_llm() # Re-inicializar con nuevos settings
        logger.info(f"Configuración del LLM actualizada - Modelo: {self.model_name}, Temperatura: {self.temperature}, Max Tokens: {self.max_tokens}")
        
    # _get_messages se simplifica, ya no usa prompt_template
    def _prepare_messages(self, system_prompt_content: str, human_prompt_content: str) -> List[Any]: # Era List[Dict[str,Any]]
        """
        Construye los mensajes para la llamada al modelo directamente desde los strings.
        """
        logger.debug(f"Preparando mensajes. System: '{system_prompt_content[:100]}...', Human: '{human_prompt_content[:100]}...'")
        return [
            SystemMessage(content=system_prompt_content),
            HumanMessage(content=human_prompt_content)
        ]
    
    @abstractmethod
    async def generate_content(self, **kwargs) -> Any:
        """
        Genera contenido. La implementación específica dependerá del agente hijo.
        Debería tomar los prompts y configuraciones necesarias.
        """
        pass
    
    async def _call_llm_with_prompts(self, system_prompt: str, human_prompt: str) -> str:
        """
        Realiza la llamada al modelo de lenguaje con prompts directos.
        """
        try:
            messages = self._prepare_messages(system_prompt_content=system_prompt, human_prompt_content=human_prompt)
            
            # --- INICIO: LÍNEA DE LOGGER SUGERIDA ---
            # Aquí puedes loggear el contenido completo del SystemMessage
            # messages[0] es el SystemMessage, messages[1] es el HumanMessage
            if messages and len(messages) > 0 and hasattr(messages[0], 'content'):
                logger.info(f"Contenido del SystemMessage enviado a ainvoke: '{messages[0].content}'")
            else:
                logger.warning("No se pudo loggear el SystemMessage: la lista de mensajes está vacía o el primer mensaje no tiene 'content'.")
            # --- FIN: LÍNEA DE LOGGER SUGERIDA ---

            logger.debug(f"Enviando mensajes al LLM: System: '{messages[0].content[:100]}...', Human: '{messages[1].content[:100]}...'")
            
            response = await self.llm.ainvoke(messages) # Usar ainvoke para async
            logger.debug(f"Respuesta recibida del LLM: '{response.content[:100]}...'")
            return response.content
            
        except Exception as e:
            logger.error(f"Error al llamar al LLM: {str(e)}", exc_info=True) # exc_info para traceback
            raise # Re-lanza la excepción para que sea manejada por el llamador

    # _call_linkedin se elimina, ya que _call_llm_with_prompts es más genérico y directo.
