# MODIFICADO: Cambiar urls_researched de List[HttpUrl] a List[str]

from pydantic import BaseModel, Field # HttpUrl ya no es necesario aquí directamente
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

# Si WebResearchOptions se define en blog.models.blog_models y se usa en el payload de entrada,
# es mejor importarlo desde allí. Si solo se usa para el tipo de web_research_options_used,
# un Dict[str, Any] es suficiente para el schema de historial.
# try:
#     from blog.models.blog_models import WebResearchOptions
# except ImportError:
#     class WebResearchOptions(BaseModel): # type: ignore
#         search_context_size: str = "medium"

class GeneratedContentBase(BaseModel):
    content_type: str 
    custom_title: Optional[str] = None
    human_prompt_used: str
    system_prompt_used: str
    model_key_selected: str 
    actual_llm_model_name_used: str 
    temperature_used: float
    max_tokens_article_used: Optional[int] = None
    max_tokens_summary_used: Optional[int] = None
    # MODIFICADO: Usar List[str] para facilitar la serialización a JSONB
    urls_researched: Optional[List[str]] = None 
    web_research_options_used: Optional[Dict[str, Any]] = None 
    pdf_filename_original: Optional[str] = None
    generated_text_main: str
    generated_text_summary: Optional[str] = None
    researched_content_summary: Optional[str] = None

class GeneratedContentCreate(GeneratedContentBase):
    pass 

class GeneratedContentResponse(GeneratedContentBase):
    content_id: uuid.UUID
    user_id: uuid.UUID 
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    class Config:
        from_attributes = True

class GeneratedContentListItemResponse(BaseModel):
    content_id: uuid.UUID
    content_type: str
    custom_title: Optional[str] = None
    human_prompt_snippet: Optional[str] = Field(None, description="Un breve extracto del prompt humano.")
    generated_text_main_snippet: Optional[str] = Field(None, description="Un breve extracto del contenido principal generado.")
    model_key_selected: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class GeneratedContentUpdate(BaseModel):
    custom_title: Optional[str] = Field(None, min_length=1, max_length=255)