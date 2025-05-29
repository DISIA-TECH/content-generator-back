# (Nuevo archivo para los modelos SQLAlchemy - deben coincidir con tu schema.sql)

from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer, ForeignKey, Table, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID 
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 
from core.database import Base 
import uuid 
from datetime import datetime

# Tabla de unión para content_tags (definida explícitamente para relaciones muchos-a-muchos)
content_tags_association = Table(
    'content_tags', Base.metadata,
    Column('content_id', PG_UUID(as_uuid=True), ForeignKey('generated_content.content_id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', PG_UUID(as_uuid=True), ForeignKey('tags.tag_id', ondelete="CASCADE"), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
)

class User(Base):
    __tablename__ = "users"

    user_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    preferred_name = Column(String(100), nullable=True) # Corregido
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    custom_prompts = relationship("UserCustomPrompt", back_populates="user", cascade="all, delete-orphan")
    generated_contents = relationship("GeneratedContent", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    preference_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    modelo_linkedin_default = Column(String(50), default='Default')
    temperatura_default_linkedin = Column(Float, default=0.7)
    modelo_blog_default = Column(String(50), default='Default')
    temperatura_default_blog = Column(Float, default=0.7)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="preferences")

class SystemPromptTemplate(Base):
    __tablename__ = "system_prompt_templates"

    template_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(100), unique=True, nullable=False, index=True)
    content_module = Column(String(50), nullable=False)
    article_type = Column(String(50), nullable=True)
    style_key = Column(String(100), nullable=False)
    display_name = Column(String(255), nullable=False)
    prompt_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint(content_module.in_(['linkedin', 'blog'])),
        CheckConstraint(article_type.in_(['general_interest', 'success_case', None])),
        # UniqueConstraint('content_module', 'article_type', 'style_key', name='uq_system_prompt_templates_module_style_key') # Ya definido en schema.sql
    )

class UserCustomPrompt(Base):
    __tablename__ = "user_custom_prompts"

    custom_prompt_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    prompt_name = Column(String(255), nullable=False)
    content_module = Column(String(50), nullable=False)
    article_type = Column(String(50), nullable=True)
    prompt_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="custom_prompts")
    
    __table_args__ = (
        CheckConstraint(content_module.in_(['linkedin', 'blog'])),
        CheckConstraint(article_type.in_(['general_interest', 'success_case', None])),
        # UniqueConstraint('user_id', 'content_module', 'article_type', 'prompt_name', name='uq_user_custom_prompts_user_module_type_name') # Ya definido
    )

class GeneratedContent(Base):
    __tablename__ = "generated_content"

    content_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)
    custom_title = Column(String(255), nullable=True)
    human_prompt_used = Column(Text, nullable=False)
    system_prompt_used = Column(Text, nullable=False)
    model_key_selected = Column(String(50), nullable=False)
    actual_llm_model_name_used = Column(String(100), nullable=False)
    temperature_used = Column(Float, nullable=False)
    max_tokens_article_used = Column(Integer, nullable=True)
    max_tokens_summary_used = Column(Integer, nullable=True)
    urls_researched = Column(JSONB, nullable=True)
    web_research_options_used = Column(JSONB, nullable=True)
    pdf_filename_original = Column(String(255), nullable=True)
    generated_text_main = Column(Text, nullable=False)
    generated_text_summary = Column(Text, nullable=True)
    researched_content_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="generated_contents")
    tags = relationship("Tag", secondary=content_tags_association, back_populates="contents")

    __table_args__ = (
        CheckConstraint(content_type.in_(['linkedin_post', 'blog_general_interest', 'blog_success_case'])),
    )


class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="tags")
    contents = relationship("GeneratedContent", secondary=content_tags_association, back_populates="tags")

    __table_args__ = (
        # UniqueConstraint('user_id', 'tag_name', name='uq_tags_user_tag_name'), # Ya definido
    )