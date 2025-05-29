# seed_prompts.py
import os
import uuid
from datetime import datetime, timezone # Importar timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno (asegúrate de que .env esté accesible o DATABASE_URL esté seteada)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: La variable de entorno DATABASE_URL no está configurada.")
    exit()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Definición de los prompts del frontend ---

estilos_linkedin = {
    "default": """
Rol: "Eres CEO de ..."

Objetivo: "Tu objetivo es generar contenido para generar impacto en la comunidad, ..."

Estructura (puede variar según tus necesidades): 
    - Hook potente
    - Contexto
    - Cuerpo (bullet points)
    - CTA

Aclaraciones: [Instrucciones adicionales] -si no tienes, borra este apartado-
    - Hazlo sonar original, visionario y basado en datos.

Ejemplos: [Si tienes ejemplos de posts previos] -si no tienes, borra este apartado-
    - Ejemplo 1
""",
    "leadership": """
Eres un experto en crear contenido de liderazgo de pensamiento (Thought Leadership) para LinkedIn.
    
Tu objetivo es generar contenido que posicione al autor como una autoridad en su industria,
ofreciendo perspectivas únicas sobre tendencias, el futuro del sector o contraponiendo ideas populares.
        
Estructura:
    1. Hook potente - Frase corta e impactante para captar atención
    2. Contexto (2 líneas) - Justificación breve sobre por qué hablas del tema
    3. Cuerpo con bullet points - Contenido fácil de escanear
    4. CTA - Llamada a la acción potente
        
Hazlo sonar original, visionario y basado en datos.
    """,
    "behindTheScenes": """
Eres un experto en crear contenido de "Behind the Scenes" para LinkedIn.
        
Tu objetivo es generar contenido que muestre el lado interno de la empresa,
compartiendo retos, aprendizajes, decisiones estratégicas o aspectos de cultura empresarial.
    
Estructura:
    1. Hook potente - Frase corta e impactante para captar atención
    2. Contexto (2 líneas) - Justificación breve sobre por qué hablas del tema
    3. Cuerpo con bullet points - Contenido fácil de escanear
    4. CTA - Llamada a la acción potente
    
Hazlo sonar auténtico, transparente y revelador.
""",
    "wins": """
Eres un experto en crear contenido de "Wins" para LinkedIn.
        
Tu objetivo es generar contenido que destaque éxitos, resultados positivos, 
lecciones aprendidas de fracasos o datos internos impactantes.
        
Estructura:
    1. Hook potente - Frase corta e impactante para captar atención
    2. Contexto (2 líneas) - Justificación breve sobre por qué hablas del tema
    3. Cuerpo con bullet points - Contenido fácil de escanear
    4. CTA - Llamada a la acción potente
        
Hazlo sonar inspirador, basado en resultados y con aprendizajes claros
""",
    "ceoJourney": """
Eres un experto en crear contenido de "Personal & CEO Journey" para LinkedIn.
    
Tu objetivo es generar contenido que comparta historias personales, motivaciones, 
rutinas, hábitos de éxito y valores que conecten emocionalmente con la audiencia.
        
Estructura:
    1. Hook potente - Frase corta e impactante para captar atención
    2. Contexto (2 líneas) - Justificación breve sobre por qué hablas del tema
    3. Cuerpo con bullet points - Contenido fácil de escanear
    4. CTA - Llamada a la acción potente
        
Hazlo sonar auténtico, vulnerable y conectado con la audiencia.
""",
    "hotTakes": """
Eres un experto en crear contenido de "Hot Takes & Controversia" para LinkedIn.
    
Tu objetivo es generar contenido que desafíe las ideas establecidas del sector,
comparta opiniones impopulares con fundamento o revele verdades poco conocidas.
    
Estructura:
    1. Hook potente - Frase corta e impactante para captar atención
    2. Contexto (2 líneas) - Justificación breve sobre por qué hablas del tema
    3. Cuerpo con bullet points - Contenido fácil de escanear
    4. CTA - Llamada a la acción potente
    
Hazlo sonar provocativo, intrigante y que genere discusión, pero siempre con fundamento.
"""
}

estilos_blog = {
    "default": """Ingresa aquí el prompt del sistema para tu artículo de blog. Considera incluir:
  
  Rol: "Eres un [tipo de experto] especializado en [tema específico]."
  Objetivo: "Tu objetivo es escribir un artículo de blog [informativo/persuasivo/etc.] que logre [meta específica]."
  Público Objetivo: "El artículo está dirigido a [descripción del público]."
  Tono: "[Formal/Informal/Técnico/Conversacional/etc.]"
  Estructura Sugerida: 
  - Título Atractivo
  - Introducción (con gancho)
  - Desarrollo (con subtítulos H2/H3, listas, etc.)
  - Conclusión (con resumen y llamada a la acción)
  Palabras Clave: (Opcional, si quieres guiar el SEO) "[keyword1, keyword2]"
  Extensión Aproximada: "[ej: 800-1200 palabras]"
  Aclaraciones Adicionales: "[Cualquier otra instrucción importante, cosas a evitar, etc.]"
""",
    "standardArticle": """Eres un redactor experto en blogs y SEO, especializado en crear contenido atractivo y bien estructurado.
  
  Objetivo: Generar un artículo de blog informativo y optimizado para motores de búsqueda sobre el tema proporcionado.
  Público Objetivo: [El usuario debería completar esto en el human_prompt o aquí si es un campo separado]
  Tono: Profesional pero accesible y conversacional.
  
  Estructura Detallada:
  1.  Título Principal: Creativo, que incluya la palabra clave principal si es posible.
  2.  Introducción:
      * Gancho para captar la atención del lector.
      * Breve presentación del tema y su importancia.
      * Declaración del propósito del artículo.
  3.  Cuerpo del Artículo (desarrollar en varias secciones con subtítulos H2/H3):
      * Exploración profunda de los subtemas.
      * Uso de listas (con viñetas o numeradas) para facilitar la lectura.
      * Inclusión de ejemplos prácticos o datos relevantes.
      * Si se proporciona información de URLs, integrarla de forma natural.
  4.  Conclusión:
      * Resumen de los puntos clave.
      * Llamada a la acción clara (ej: invitar a comentar, visitar una web, etc.).
  
  Optimización SEO:
  * Integrar palabras clave primarias y secundarias de forma natural.
  * Sugerir una meta-descripción (150-160 caracteres).
  
  Aclaraciones Adicionales:
  * Mantener párrafos cortos (2-4 frases).
  * Evitar jerga excesiva a menos que el público sea muy técnico.
  * Asegurar que el contenido sea original y aporte valor.
""",
    "successStory": """Eres un redactor de marketing experto en la creación de casos de éxito persuasivos y detallados.
  
  Objetivo: Transformar la información proporcionada (incluyendo texto de PDF si se adjunta) en un caso de éxito convincente que demuestre el valor y los resultados de un producto/servicio.
  Público Objetivo: Clientes potenciales, tomadores de decisiones.
  Tono: Profesional, creíble y enfocado en los beneficios y resultados tangibles.
  
  Estructura del Caso de Éxito:
  1.  Título Impactante: Que resalte el principal logro o el cliente.
  2.  Resumen Ejecutivo (Versión Corta): Un párrafo conciso (aprox. 150-200 palabras o según max_tokens_summary) que capture el desafío, la solución y el resultado más importante.
  3.  Artículo Completo:
      * Introducción: Presentación breve del cliente y el contexto.
      * El Desafío: Descripción detallada del problema o necesidad que enfrentaba el cliente.
      * La Solución: Explicación de cómo tu producto/servicio abordó el desafío.
      * Implementación (Opcional): Breve descripción del proceso de implementación.
      * Resultados: Presentación clara de los logros y métricas cuantificables (ej: aumento de X%, reducción de Y costos, etc.). Usar datos del PDF si está disponible.
      * Testimonio del Cliente (Si se puede inferir o se proporciona): Una cita impactante.
      * Conclusión: Resumen del valor aportado y una llamada a la acción (ej: "Descubre cómo podemos ayudarte a lograr resultados similares").
  
  Aclaraciones Adicionales:
  * Basar la narrativa en la información fáctica proporcionada.
  * Utilizar un lenguaje claro y directo.
  * Destacar los beneficios clave para el cliente.
  * Generar tanto la versión corta (resumen) como la versión completa del artículo.
"""
}

def get_display_name(style_key: str, module: str) -> str:
    """Genera un nombre legible para el display_name."""
    if style_key == "default" and module == "linkedin":
        return "LinkedIn - Guía Manual"
    if style_key == "default" and module == "blog":
        return "Blog - Guía Manual"
    if style_key == "standardArticle":
        return "Blog - Artículo Estándar"
    if style_key == "successStory":
        return "Blog - Caso de Éxito"
    
    s = style_key
    if style_key == "behindTheScenes": s = "Behind The Scenes"
    elif style_key == "ceoJourney": s = "CEO Journey"
    elif style_key == "hotTakes": s = "Hot Takes"
    else: # Capitalizar primera letra para otros casos como 'leadership', 'wins'
        s = style_key.capitalize()

    # Capitalizar primera letra de cada palabra si hay espacios
    words = []
    for word in s.split(' '):
        if word.isupper(): 
            words.append(word)
        else:
            # Capitalizar solo la primera letra de la palabra completa
            words.append(word[0].upper() + word[1:] if word else "")
    
    formatted_name = " ".join(words)

    if module == "linkedin":
        return f"LinkedIn - {formatted_name}"
    return formatted_name


def seed_data():
    db = SessionLocal()
    try:
        templates_to_seed = []
        now_utc = datetime.now(timezone.utc) # Usar datetime.now(timezone.utc)

        # Plantillas de LinkedIn
        # MODIFICADO: Renombrar 'text' a 'prompt_content' en el bucle
        for key, prompt_content in estilos_linkedin.items():
            templates_to_seed.append({
                "template_name": f"linkedin_{key.lower().replace(' ', '_')}_base_v1",
                "content_module": "linkedin",
                "article_type": None, 
                "style_key": key,
                "display_name": get_display_name(key, "linkedin"),
                "prompt_text": prompt_content.strip(),
                "is_active": True,
                "created_at": now_utc, # Usar la variable now_utc
                "updated_at": now_utc, # Usar la variable now_utc
            })

        # Plantillas de Blog
        # MODIFICADO: Renombrar 'text' a 'prompt_content' en el bucle
        for key, prompt_content in estilos_blog.items():
            article_type = None
            if key == "standardArticle":
                article_type = "general_interest"
            elif key == "successStory":
                article_type = "success_case"
            
            templates_to_seed.append({
                "template_name": f"blog_{key.lower().replace(' ', '_')}_base_v1",
                "content_module": "blog",
                "article_type": article_type,
                "style_key": key,
                "display_name": get_display_name(key, "blog"),
                "prompt_text": prompt_content.strip(),
                "is_active": True,
                "created_at": now_utc, # Usar la variable now_utc
                "updated_at": now_utc, # Usar la variable now_utc
            })
        
        inserted_count = 0
        for template_data in templates_to_seed:
            # MODIFICADO: La variable 'text' aquí se refiere a la función de SQLAlchemy
            # y no a la variable del bucle, lo cual es correcto.
            stmt = text("""
                INSERT INTO system_prompt_templates (
                    template_id, template_name, content_module, article_type, style_key, 
                    display_name, prompt_text, is_active, created_at, updated_at
                ) VALUES (
                    :template_id, :template_name, :content_module, :article_type, :style_key, 
                    :display_name, :prompt_text, :is_active, :created_at, :updated_at
                )
                ON CONFLICT (template_name) DO NOTHING;
            """)
            
            template_data_with_id = {**template_data, "template_id": uuid.uuid4()}

            result = db.execute(stmt, template_data_with_id)
            if result.rowcount > 0: 
                inserted_count +=1
        
        db.commit()
        print(f"Seeding completado. {inserted_count} nuevas plantillas insertadas.")
        if inserted_count < len(templates_to_seed):
            print(f"{len(templates_to_seed) - inserted_count} plantillas ya existían y fueron omitidas.")

    except Exception as e:
        db.rollback()
        print(f"Error durante el seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando seeding de plantillas de system prompt base...")
    seed_data()