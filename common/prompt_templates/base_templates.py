from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BasePromptTemplate(ABC):
    """Clase base para todas las plantillas de prompts."""
    
    @abstractmethod
    def get_system_message(self) -> str:
        """Obtiene el mensaje del sistema que define el rol y comportamiento."""
        pass
    
    @abstractmethod
    def get_human_template(self) -> str:
        """Obtiene la plantilla para el mensaje del usuario."""
        pass
    
    def get_prompt_data(self) -> Dict[str, str]:
        """Obtiene los datos completos del prompt."""
        return {
            "system_message": self.get_system_message(),
            "human_template": self.get_human_template()
        }


class ContentPromptTemplate(BasePromptTemplate):
    """Plantilla base para prompts de generación de contenido."""
    
    
    def __init__(
        self, 
        role_description: Optional[str] = None,
        content_objective: Optional[str] = None,
        style_guidance: Optional[str] = None,
        structure_description: str = "",
        tone: Optional[str] = None,
        format_guide: Optional[str] = None,
        seo_guidelines: Optional[str] = None,
        limitations: Optional[str] = None,
        required_length: Optional[str] = None,
        additional_instructions: Optional[str] = None
    ):
        """
        Inicializa la plantilla con los componentes necesarios.
        
        Args:
            role_description: Descripción del rol que asume el modelo
            content_objective: Objetivo del contenido a generar
            style_guidance: Guía de estilo para el contenido
            structure_description: Descripción de la estructura del contenido
            tone: Tono a utilizar en el contenido
            format_guide: Guía de formato para el contenido
            seo_guidelines: Directrices de SEO
            limitations: Limitaciones a considerar
            additional_instructions: Instrucciones adicionales opcionales
        """
        self.role_description = role_description
        self.content_objective = content_objective
        self.style_guidance = style_guidance
        self.structure_description = structure_description
        self.tone = tone
        self.format_guide = format_guide
        self.seo_guidelines = seo_guidelines
        self.limitations = limitations
        self.required_length = required_length
        self.additional_instructions = additional_instructions
    
    def get_system_message(self) -> str:
        """Construye un mensaje del sistema estructurado."""
        
        system_message = f"""ROL: {self.role_description}
OBJETIVO: {self.content_objective}
"""
        
        if self.tone:
            system_message += f"""TONO:
{self.tone}
"""
        
        system_message += f"""ESTRUCTURA:
{self.structure_description}
"""
        
        if self.format_guide:
            system_message += f"""FORMATO:
{self.format_guide}
"""
        
        if self.limitations:
            system_message += f"""LIMITACIONES:
{self.limitations}
"""
            
        if self.seo_guidelines:
            system_message += f"""OPTIMIZACIÓN SEO:
{self.seo_guidelines}
"""
         
        if self.style_guidance:
            system_message += f"""ESTILO:
{self.style_guidance}
"""
            
        system_message += f"""REQUISITO DE LONGITUD:
{self.required_length}
"""
            
        if self.additional_instructions:
            system_message += f"\n\n{self.additional_instructions}"
            
        return system_message
    
    def get_human_template(self) -> str:
        """Proporciona una plantilla genérica para el mensaje del usuario."""
        return """Genera contenido sobre el tema: {tema}

Comentarios adicionales: {comentarios_adicionales}
"""


class PromptBuilder:
    """Utilidad para construir prompts complejos a partir de componentes."""
    
    def __init__(self):
        self.system_components = []
        self.human_components = []
    
    def add_system_component(self, component: str) -> 'PromptBuilder':
        """Añade un componente al mensaje del sistema."""
        self.system_components.append(component)
        return self
    
    def add_human_component(self, component: str) -> 'PromptBuilder':
        """Añade un componente al mensaje del usuario."""
        self.human_components.append(component)
        return self
    
    def build(self) -> Dict[str, str]:
        """Construye el prompt completo."""
        return {
            "system_message": "\n\n".join(self.system_components),
            "human_template": "\n\n".join(self.human_components)
        }