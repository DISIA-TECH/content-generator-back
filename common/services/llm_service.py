# from typing import Dict, Any, List, Optional, Union
# from langchain.schema import HumanMessage, SystemMessage, AIMessage, FunctionMessage
# from langchain_openai import ChatOpenAI
# from core.config import settings
# from core.logger import get_logger
# 
# logger = get_logger("llm_service")
# 
# 
# class LLMService:
#     """Servicio para interactuar con los modelos de lenguaje."""
#     
#     def __init__(
#         self,
#         model: str = settings.OPENAI_MODEL,
#         temperature: float = settings.DEFAULT_TEMPERATURE
#     ):
#         """
#         Inicializa el servicio LLM.
#         
#         Args:
#             model: Modelo de lenguaje a utilizar
#             temperature: Temperatura para la generación
#         """
#         self.model = model
#         self.temperature = temperature
#         self.llm = self._initialize_llm()
#     
#     def _initialize_llm(self) -> ChatOpenAI:
#         """
#         Inicializa el modelo de lenguaje.
#         
#         Returns:
#             ChatOpenAI: Instancia del modelo configurado
#         """
#         logger.info(f"Inicializando LLM con modelo: {self.model}, temperatura: {self.temperature}")
#         logger.info(f"Aca estan pasando cosas: {self.model}, temperatura: {self.temperature}")
#         return ChatOpenAI(
#             model=self.model,
#             temperature=self.temperature,
#             api_key=settings.OPENAI_API_KEY
#         )
#     
#     def update_settings(self, model: Optional[str] = None, temperature: Optional[float] = None) -> None:
#         """
#         Actualiza la configuración del modelo.
#         
#         Args:
#             model: Nuevo modelo a utilizar (opcional)
#             temperature: Nueva temperatura a utilizar (opcional)
#         """
#         if model:
#             self.model = model
#         
#         if temperature is not None:
#             self.temperature = temperature
#             
#         self.llm = self._initialize_llm()
#         logger.info(f"Configuración del modelo actualizada - Modelo: {self.model}, Temperatura: {self.temperature}")
#     
#     async def generate_content(
#         self,
#         system_message: str,
#         human_message: str,
#         functions: Optional[List[Dict[str, Any]]] = None
#     ) -> Union[str, Dict[str, Any]]:
#         """
#         Genera contenido usando el LLM.
#         
#         Args:
#             system_message: Mensaje del sistema
#             human_message: Mensaje del usuario
#             functions: Definiciones de funciones para function calling (opcional)
#             
#         Returns:
#             Union[str, Dict[str, Any]]: Respuesta del modelo o resultado de function call
#         """
#         try:
#             messages = [
#                 SystemMessage(content=system_message),
#                 HumanMessage(content=human_message)
#             ]
#             
#             if functions:
#                 self.llm = self._initialize_llm()
#                 # Configurar function calling
#                 self.llm.model_kwargs = {"functions": functions}
#             
#             logger.debug(f"Enviando mensaje al LLM con {len(messages)} mensajes")
#             response = await self.llm.ainvoke(messages)
#             
#             return response.content
#             
#         except Exception as e:
#             logger.error(f"Error al generar contenido con LLM: {str(e)}")
#             raise
#     
#     async def generate_with_history(
#         self,
#         messages: List[Union[SystemMessage, HumanMessage, AIMessage, FunctionMessage]],
#         functions: Optional[List[Dict[str, Any]]] = None
#     ) -> Union[str, Dict[str, Any]]:
#         """
#         Genera contenido usando el LLM con un historial de mensajes.
#        
#         Args:
#             messages: Lista de mensajes que representan la conversación
#             functions: Definiciones de funciones para function calling (opcional)
#             
#         Returns:
#             Union[str, Dict[str, Any]]: Respuesta del modelo o resultado de function call
#         """
#         try:
#             if functions:
#                 self.llm = self._initialize_llm()
#                 # Configurar function calling
#                 self.llm.model_kwargs = {"functions": functions}
#             
#             logger.debug(f"Enviando conversación al LLM con {len(messages)} mensajes")
#             response = await self.llm.ainvoke(messages)
#             
#             return response.content
#             
#         except Exception as e:
#             logger.error(f"Error al generar contenido con historial en LLM: {str(e)}")
#             raise