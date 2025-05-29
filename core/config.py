# backend/core/config.py
# (Actualizado para incluir DATABASE_URL y configuraciones JWT)
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Content Generator API"
    PROJECT_DESCRIPTION: str = "API para generar contenido estratégico para LinkedIn y Blog usando agentes especializados"
    PROJECT_VERSION: str = "0.1.0"
    
    API_V1_STR: str = "/api/v1"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o") 
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "2000")) 

    MODEL_GPT4O: str = "gpt-4o" 
    MODEL_PABLO_FINETUNED: str = os.getenv("MODEL_PABLO_FINETUNED", "ft:gpt-4o-2024-08-06:disia:pablo-estilo-v1:BS3tYmqt") 
    MODEL_AITOR_FINETUNED: str = os.getenv("MODEL_AITOR_FINETUNED", "ft:gpt-3.5-turbo:my-org:aitor-model:xxxxxxx")
    MODEL_WEB_SEARCH: str = os.getenv("MODEL_WEB_SEARCH", "gpt-4o") 

    MODEL_MAPPING: Dict[str, str] = {
        "Default": MODEL_GPT4O,
        "Pablo": MODEL_PABLO_FINETUNED,
        "Aitor": MODEL_AITOR_FINETUNED,
    }
    
    # Configuraciones de Base de Datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://app_user:123456@localhost:5432/content_generator_db")
    
    # Configuraciones JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tu_super_secreto_aqui_cambialo") # ¡CAMBIA ESTO EN PRODUCCIÓN!
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    DEFAULT_BLOG_AGENT_CONFIG: Dict[str, Any] = {
        "role_description": "especialista en creación de contenidos para blogs",
        "content_objective": "generar artículos completos, informativos y atractivos",
    }
    
    DEFAULT_LINKEDIN_AGENT_CONFIG: Dict[str, Any] = { 
        "role_description": "especialista en creación de contenido para LinkedIn",
        "content_objective": "generar publicaciones virales y de alto impacto",
    }
    
    model_config = { 
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8", # Añadido para asegurar codificación correcta
        "extra": "ignore" 
    }

settings = Settings()