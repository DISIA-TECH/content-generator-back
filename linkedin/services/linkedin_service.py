# MODIFICADO: Para aceptar user_id y guardar en el historial

from sqlalchemy.orm import Session # Para type hinting
import uuid # Para type hinting del user_id

from linkedin.agents.linkedin_agent import LinkedInAgent
from linkedin.models.linkedin_models import LinkedInPostRequestRefactored, LinkedInPostResponseRefactored
from core.logger import get_logger
from core.config import settings
# Nuevas importaciones
from crud import content_crud # Para guardar el historial
from schemas.content_schemas import GeneratedContentCreate # Para el payload del historial

logger = get_logger("linkedin_service")

class LinkedInService:
    def __init__(self):
        logger.info("LinkedInService inicializado.")
        # El agente se instancia por solicitud ahora

    async def generate_post_service_method(
        self, 
        request: LinkedInPostRequestRefactored,
        db: Session, # Añadir sesión de BD
        user_id: uuid.UUID # Añadir user_id
    ) -> LinkedInPostResponseRefactored:
        logger.info(f"Servicio: Generando post de LinkedIn. Tema='{request.human_prompt[:50]}...', Modelo='{request.model}'")
        try:
            agent = LinkedInAgent(
                model_identifier=request.model,
                temperature=request.temperature
                # max_tokens no es un param directo en LinkedInPostRequestRefactored, se usa el default del agente
            )
            
            # El método del agente ahora se llama generate_post_refactored
            # y espera LinkedInPostRequestRefactored
            response_data = await agent.generate_post_refactored(request) # El agente ya devuelve el response_model

            # Guardar en el historial
            content_to_save = GeneratedContentCreate(
                content_type='linkedin_post',
                custom_title=request.human_prompt[:100], # Usar el inicio del prompt como título por defecto
                human_prompt_used=request.human_prompt,
                system_prompt_used=agent._apply_author_prefix_to_system_prompt(request.system_prompt), # El system prompt final usado
                model_key_selected=request.model,
                actual_llm_model_name_used=agent.model_name, # El modelo real del LLM usado por el agente
                temperature_used=agent.temperature,
                generated_text_main=response_data.generated_post
                # Otros campos opcionales (urls_researched, etc.) son None por defecto
            )
            content_crud.create_generated_content(db=db, user_id=user_id, content_data=content_to_save)
            logger.info(f"Post de LinkedIn guardado en el historial para el usuario {user_id}")

            return response_data # Devolver la respuesta original del agente
            
        except ValueError as ve:
             logger.error(f"Servicio LinkedIn: Error de configuración al generar post: {str(ve)}", exc_info=True)
             raise 
        except Exception as e:
            logger.error(f"Servicio LinkedIn: Error al generar post: {str(e)}", exc_info=True)
            raise