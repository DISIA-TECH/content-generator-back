from typing import Dict, Any, Optional
from common.prompt_templates.base_templates import ContentPromptTemplate
from core.logger import get_logger
from core.config import settings
from linkedin.models.linkedin_models import LinkedInPostStyle, LinkedInAuthor

logger = get_logger("linkedin_prompts")


class LinkedInPromptTemplate(ContentPromptTemplate):
    """Plantilla base para prompts de LinkedIn."""
    
    def __init__(
        self,
        role_description: str = "especialista en creación de contenido para LinkedIn",
        content_objective: str = "generar publicaciones profesionales con alto engagement",
        style_guidance: str = "Profesional pero conversacional, incluye emojis estratégicamente",
        structure_description: str = "Utiliza párrafos cortos, llamada a la acción al final",
        tone: str = "Profesional con toque personal y conversacional",
        format_guide: str = "- Párrafos cortos (1-3 líneas máximo)\n- Utiliza espacios entre párrafos\n- Incluye emojis relevantes\n- Considera usar líneas para separar secciones\n- Usa hashtags relevantes al final",
        engagement_tips: str = "- Comienza con una pregunta o dato sorprendente\n- Cuenta una historia personal o profesional breve\n- Incluye una reflexión que inspire a comentar\n- Termina con una llamada a la acción clara",
        limitations: str = "- Evita contenido excesivamente promocional\n- No uses más de 3-4 hashtags\n- Evita textos demasiado largos\n- No uses jerga excesivamente técnica",
        additional_instructions: Optional[str] = None
    ):
        """Inicializa la plantilla con valores por defecto."""
        super().__init__(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            limitations=limitations,
            additional_instructions=additional_instructions
        )
        self.engagement_tips = engagement_tips
    
    def get_system_message(self) -> str:
        """Construye un mensaje del sistema estructurado."""
        system_message = super().get_system_message()
        
        return system_message
    
    def get_human_template(self) -> str:
        """Proporciona una plantilla para el mensaje del usuario."""
        return """Tema: {tema}

Información adicional: {informacion_adicional}

Genera un post de LinkedIn profesional sobre el tema indicado.
"""


class LeadershipPromptTemplate(LinkedInPromptTemplate):
    """Plantilla para posts de liderazgo."""
    
    def __init__(
        self,
        role_description: str = "líder visionario y estratega empresarial",
        content_objective: str = "compartir perspectivas estratégicas que inspiren a otros líderes",
        style_guidance: str = "Visionario, inspirador y orientado a resultados",
        structure_description: str = "- Comienza con una reflexión profunda o lección aprendida\n- Desarrolla una idea estratégica clave\n- Comparte perspectivas que desafíen el pensamiento convencional\n- Termina con una pregunta reflexiva o llamada a la acción inspiradora",
        tone: str = "Autoritativo pero accesible, con enfoque en el valor estratégico",
        format_guide: str = "- Párrafos concisos y poderosos\n- Utiliza una o dos frases impactantes\n- Incluye una metáfora o analogía potente\n- Un emoji estratégicamente colocado puede añadir personalidad",
        engagement_tips: str = "- Comparte una lección de liderazgo personal\n- Menciona un desafío superado\n- Habla de tendencias futuras en tu industria\n- Pide opiniones sobre enfoques estratégicos",
        additional_instructions: str = "Muestra confianza y visión sin arrogancia. Mantén un balance entre sabiduría compartida y humildad."
    ):
        """Inicializa la plantilla para posts de liderazgo."""
        super().__init__(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            engagement_tips=engagement_tips,
            additional_instructions=additional_instructions
        )

    def get_system_message(self) -> str:
        """Construye solo la parte de estructura para LinkedIn."""
        return self.structure_description
    
    def get_human_template(self) -> str:
        """Proporciona una plantilla específica para posts de liderazgo."""
        return """Tema: {tema}"""


class BehindTheScenesPromptTemplate(LinkedInPromptTemplate):
    """Plantilla para posts de 'Behind the Scenes'."""
    
    def __init__(
        self,
        role_description: str = "líder transparente que comparte el día a día empresarial",
        content_objective: str = "humanizar la marca mostrando los procesos internos y el trabajo cotidiano",
        style_guidance: str = "Auténtico, cercano y revelador, mostrando aspectos normalmente no visibles",
        structure_description: str = "- Comienza contextualizando la situación o momento\n- Describe el proceso o la situación interna\n- Comparte aprendizajes o reflexiones personales\n- Conecta con valores o misión de la empresa\n- Termina con una nota personal o pregunta",
        tone: str = "Conversacional, honesto y transparente",
        format_guide: str = "- Estilo narrativo y personal\n- Usa primera persona\n- Incluye detalles específicos que den autenticidad\n- Emojis que transmitan emociones reales\n- Considera mencionar a miembros del equipo",
        engagement_tips: str = "- Comparte un desafío y cómo se superó\n- Muestra el antes/después de un proceso\n- Habla sobre errores y aprendizajes\n- Pide opiniones sobre decisiones o enfoques",
        additional_instructions: str = "Busca el balance entre transparencia y profesionalismo. Muestra vulnerabilidad pero mantén una imagen de competencia."
    ):
        """Inicializa la plantilla para posts de 'Behind the Scenes'."""
        super().__init__(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            engagement_tips=engagement_tips,
            additional_instructions=additional_instructions
        )
    
    def get_human_template(self) -> str:
        """Proporciona una plantilla específica para posts de 'Behind the Scenes'."""
        return """Tema: {tema}

Información adicional: {informacion_adicional}

Genera un post de LinkedIn que muestre el "detrás de escena" relacionado con el tema. 
Revela procesos internos, desafíos cotidianos o momentos no visibles habitualmente, creando una sensación de acceso privilegiado.
"""


class WinsPromptTemplate(LinkedInPromptTemplate):
    """Plantilla para posts de celebración de logros."""
    
    def __init__(
        self,
        role_description: str = "líder que celebra logros y reconoce contribuciones",
        content_objective: str = "compartir y celebrar éxitos, hitos y reconocimientos de manera inspiradora",
        style_guidance: str = "Celebratorio, orgulloso pero humilde, enfocado en el impacto",
        structure_description: str = "- Anuncia el logro o reconocimiento claramente\n- Proporciona contexto sobre su importancia\n- Reconoce a las personas involucradas\n- Comparte lecciones o factores de éxito\n- Expresa gratitud y proyecta hacia el futuro",
        tone: str = "Entusiasta, genuinamente orgulloso y agradecido",
        format_guide: str = "- Frases contundentes y celebratorias\n- Usa emojis festivos estratégicamente\n- Incluye números o métricas cuando sea relevante\n- Considera mencionar y etiquetar a personas clave\n- Usa signos de exclamación con moderación",
        engagement_tips: str = "- Comparte el camino hacia el logro, no solo el resultado\n- Menciona obstáculos superados\n- Expresa gratitud específica\n- Invita a otros a compartir sus propios éxitos",
        additional_instructions: str = "Equilibra la celebración con humildad. Destaca los logros sin parecer presumido, y siempre reconoce el esfuerzo colectivo."
    ):
        """Inicializa la plantilla para posts de celebración de logros."""
        super().__init__(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            engagement_tips=engagement_tips,
            additional_instructions=additional_instructions
        )
    
    def get_human_template(self) -> str:
        """Proporciona una plantilla específica para posts de celebración de logros."""
        return """Tema: {tema}

Información adicional: {informacion_adicional}

Genera un post de LinkedIn que celebre un logro, hito o reconocimiento relacionado con el tema. 
Expresa orgullo por el resultado alcanzado mientras reconoces el esfuerzo y las contribuciones que lo hicieron posible.
"""


class CEOJourneyPromptTemplate(LinkedInPromptTemplate):
    """Plantilla para posts sobre el viaje del CEO."""
    
    def __init__(
        self,
        role_description: str = "CEO que comparte su trayectoria y experiencias de liderazgo",
        content_objective: str = "narrar experiencias personales de liderazgo que inspiren y eduquen",
        style_guidance: str = "Narrativo, reflexivo y personal, con enfoque en el crecimiento",
        structure_description: str = "- Comienza con un momento decisivo o desafiante\n- Narra la experiencia o lección aprendida\n- Reflexiona sobre el impacto en tu liderazgo\n- Conecta con principios o valores\n- Comparte una conclusión o consejo derivado",
        tone: str = "Auténtico, reflexivo y vulnerable pero seguro",
        format_guide: str = "- Estilo narrativo con arco claro\n- Primera persona y lenguaje personal\n- Incluye detalles específicos que den autenticidad\n- Considera usar una estructura temporal (antes/después)\n- Emojis que transmitan emociones genuinas",
        engagement_tips: str = "- Comparte un fracaso y cómo te transformó\n- Menciona mentores o influencias clave\n- Describe un momento de duda o pivot\n- Pregunta por experiencias similares",
        additional_instructions: str = "Muestra vulnerabilidad auténtica balanceada con resiliencia. El objetivo es inspirar mostrando tanto los desafíos como las superaciones."
    ):
        """Inicializa la plantilla para posts sobre el viaje del CEO."""
        super().__init__(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            engagement_tips=engagement_tips,
            additional_instructions=additional_instructions
        )
    
    def get_human_template(self) -> str:
        """Proporciona una plantilla específica para posts sobre el viaje del CEO."""
        return """Tema: {tema}

Información adicional: {informacion_adicional}

Genera un post de LinkedIn que relate una experiencia personal de liderazgo relacionada con el tema.
Narra un momento significativo de tu trayectoria como CEO, compartiendo lecciones y reflexiones personales.
"""


class HotTakesPromptTemplate(LinkedInPromptTemplate):
    """Plantilla para posts de opiniones provocativas."""
    
    def __init__(
        self,
        role_description: str = "líder de opinión que desafía el pensamiento convencional",
        content_objective: str = "presentar perspectivas contraintuitivas o disruptivas que generen debate",
        style_guidance: str = "Provocativo, disruptivo y desafiante, pero fundamentado",
        structure_description: str = "- Comienza con una afirmación contundente y sorprendente\n- Desafía una creencia o práctica establecida\n- Argumenta tu posición con ejemplos o lógica\n- Anticipa y responde a potenciales objeciones\n- Invita al debate con una pregunta o reto",
        tone: str = "Asertivo, seguro y ligeramente provocador",
        format_guide: str = "- Frases cortas e impactantes\n- Usa párrafos concisos\n- Incluye al menos una afirmación controversial\n- Considera usar formato numerado para puntos clave\n- Limita los emojis para mantener seriedad",
        engagement_tips: str = "- Cuestiona una práctica común en la industria\n- Contradice una 'verdad' aceptada\n- Usa frases como '¿Impopular opinión?'\n- Termina con '¿Estás de acuerdo o en desacuerdo?'",
        additional_instructions: str = "Sé provocativo pero siempre mantén el profesionalismo. No seas controversial solo por serlo; asegúrate de tener argumentos sólidos detrás de tus afirmaciones."
    ):
        """Inicializa la plantilla para posts de opiniones provocativas."""
        super().__init__(
            role_description=role_description,
            content_objective=content_objective,
            style_guidance=style_guidance,
            structure_description=structure_description,
            tone=tone,
            format_guide=format_guide,
            engagement_tips=engagement_tips,
            additional_instructions=additional_instructions
        )
    
    def get_human_template(self) -> str:
        """Proporciona una plantilla específica para posts de opiniones provocativas."""
        return """Tema: {tema}

Información adicional: {informacion_adicional}

Genera un post de LinkedIn con una perspectiva provocativa o contraintuitiva sobre el tema.
Desafía el pensamiento convencional y presenta una opinión que pueda generar debate, manteniendo un tono profesional.
"""


def get_prompt_template_for_style(style: LinkedInPostStyle) -> LinkedInPromptTemplate:
    """
    Devuelve la plantilla de prompt adecuada según el estilo seleccionado.
    
    Args:
        style: Estilo de post de LinkedIn
        
    Returns:
        LinkedInPromptTemplate: Plantilla específica para el estilo
    """
    style_templates = {
        LinkedInPostStyle.LEADERSHIP: LeadershipPromptTemplate(),
        LinkedInPostStyle.BEHIND_THE_SCENES: BehindTheScenesPromptTemplate(),
        LinkedInPostStyle.WINS: WinsPromptTemplate(),
        LinkedInPostStyle.CEO_JOURNEY: CEOJourneyPromptTemplate(),
        LinkedInPostStyle.HOT_TAKES: HotTakesPromptTemplate()
    }
    
    return style_templates.get(style, LinkedInPromptTemplate())


def get_author_system_prompt(author: LinkedInAuthor) -> str:
    """
    Devuelve instrucciones específicas para emular el estilo de un autor.
    
    Args:
        author: Autor a emular
        
    Returns:
        str: Instrucciones para emular al autor
    """
    author_prompts = {
        LinkedInAuthor.PABLO: """Emula el estilo de escritura de Pablo, caracterizado por:
- Tono visionario y estratégico
- Uso ocasional de anglicismos técnicos
- Párrafos cortos con ideas potentes
- Menciones frecuentes a innovación y transformación
- Balance entre profesionalismo y cercanía
- Uso selectivo de emojis estratégicos
- Preguntas reflexivas al final""",
        
        LinkedInAuthor.AITOR: """Emula el estilo de escritura de Aitor, caracterizado por:
- Tono directo y práctico
- Enfoque en resultados tangibles
- Uso de ejemplos concretos y datos
- Párrafos estructurados lógicamente
- Estilo conciso y claro
- Referencias ocasionales a experiencias personales
- Llamadas a la acción específicas"""
    }
    
    return author_prompts.get(author, "")