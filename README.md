# Content Generator API

API para generar contenidos de blog y LinkedIn utilizando IA, con arquitectura limpia y modular.

## Descripción

Este proyecto es una aplicación backoffice que permite a un CEO generar dos tipos de contenido:
- Artículos de blog (de interés general o casos de éxito)
- Posts para LinkedIn

La aplicación permite personalizar los prompts y parámetros de generación de contenido desde el frontend.

## Tecnologías utilizadas

- **Python**: Lenguaje principal de programación
- **FastAPI**: Framework para construcción de APIs
- **LangChain**: Framework para aplicaciones de IA
- **OpenAI**: Proveedor de modelos de lenguaje
- **Pydantic**: Validación de datos y configuraciones
- **Logging**: Sistema de registro

## Estructura del proyecto
```
content-generator/
├── api/                # Capa de API
├── blog/               # Módulo para generación de artículos de blog
├── linkedin/           # Módulo para generación de posts de LinkedIn
├── common/             # Componentes compartidos
├── core/               # Configuraciones centrales
├── tests/              # Tests unitarios e integración
└── requirements.txt    # Dependencias del proyecto
```
## Características principales

### Generador de artículos de blog

- **Tipos de artículos**:
  - **Interés general**: Artículos sobre temas específicos con referencias a URLs externas
  - **Casos de éxito**: Artículos basados en información proporcionada en PDFs

### Generador de posts para LinkedIn (próximamente)

- Generación de contenido optimizado para la plataforma LinkedIn
- Personalización de tono, estilo y estructura

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/content-generator.git
cd content-generator
```
2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Crear archivo .env con las configuraciones necesarias
OPENAI_API_KEY=tu_clave_api_openai
HOST=0.0.0.0
PORT=8001
DEBUG=True

## Uso
### Iniciar el servidor
```bash
python -m api.main
```

La API estará disponible en http://localhost:8001

### Documentación de la API
La documentación interactiva estará disponible en:
- Swagger UI: http://localhost:8001/api/v1/docs
- ReDoc: http://localhost:8001/api/v1/redoc

## Ejemplos de uso
### Generar un artículo de interés general

POST /api/v1/blog/generate/general-interest

Body:
```json
{
  "tema": "Inteligencia Artificial en el marketing digital",
  "palabras_clave_primarias": ["IA", "marketing digital"],
  "palabras_clave_secundarias": ["ROI", "automatización"],
  "longitud": "1000-1500 palabras",
  "publico_objetivo": "Profesionales de marketing",
  "objetivo": "Informar",
  "tono_especifico": "Profesional con toque conversacional",
  "llamada_accion": "Contactar para asesoría",
  "urls_referencia": ["https://example.com/articulo"],
  "system_components": {
    "role_description": "especialista en marketing digital",
    "content_objective": "informar sobre aplicaciones de IA",
    "tone": "Profesional pero accesible"
  }
}
```
