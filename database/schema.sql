-- Habilitar la extensión para generar UUIDs si no está habilitada
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla para los usuarios de la aplicación
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    preferred_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
    -- Podrías añadir un campo 'salt' aquí si tu estrategia de hasheo lo requiere externamente,
    -- pero passlib con bcrypt usualmente maneja el salt dentro del hash.
);

-- Tabla para las preferencias de usuario (ej. modelos por defecto)
CREATE TABLE user_preferences (
    preference_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    modelo_linkedin_default VARCHAR(50) DEFAULT 'Default',
    temperatura_default_linkedin FLOAT DEFAULT 0.7,
    modelo_blog_default VARCHAR(50) DEFAULT 'Default',
    temperatura_default_blog FLOAT DEFAULT 0.7,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Tabla para las plantillas de System Prompt BASE (globales, definidas por el administrador)
CREATE TABLE system_prompt_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(100) UNIQUE NOT NULL, -- Identificador interno único, ej. "linkedin_leadership_base"
    content_module VARCHAR(50) NOT NULL CHECK (content_module IN ('linkedin', 'blog')), -- 'linkedin', 'blog'
    article_type VARCHAR(50) CHECK (article_type IN ('general_interest', 'success_case', NULL)), -- Para blogs, NULL para LinkedIn
    style_key VARCHAR(100) NOT NULL, -- La clave que usa el frontend, ej. "leadership", "standardArticle", "default"
    display_name VARCHAR(255) NOT NULL, -- Nombre que ve el usuario en el menú, ej. "Liderazgo de Pensamiento"
    prompt_text TEXT NOT NULL, -- El contenido del system prompt
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
    -- CONSTRAINT unique_style_per_module_type UNIQUE (content_module, article_type, style_key) -- Asegura unicidad
);

-- Tabla para los System Prompts PERSONALIZADOS por cada usuario
CREATE TABLE user_custom_prompts (
    custom_prompt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    prompt_name VARCHAR(255) NOT NULL, -- Nombre que el usuario le da a su plantilla
    content_module VARCHAR(50) NOT NULL CHECK (content_module IN ('linkedin', 'blog')),
    article_type VARCHAR(50) CHECK (article_type IN ('general_interest', 'success_case', NULL)), -- Para blogs, NULL para LinkedIn
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT unique_user_prompt_name UNIQUE (user_id, content_module, article_type, prompt_name)
);

-- Tabla para el HISTORIAL de contenido generado
CREATE TABLE generated_content (
    content_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('linkedin_post', 'blog_general_interest', 'blog_success_case')),
    custom_title VARCHAR(255), -- Título opcional dado por el usuario al guardar en historial

    -- Parámetros de generación usados
    human_prompt_used TEXT NOT NULL,
    system_prompt_used TEXT NOT NULL,
    model_key_selected VARCHAR(50) NOT NULL, -- "Default", "Pablo", "Aitor"
    actual_llm_model_name_used VARCHAR(100) NOT NULL, -- ej. "gpt-4o", "ft:gpt-3.5..."
    temperature_used FLOAT NOT NULL,
    max_tokens_article_used INTEGER,
    max_tokens_summary_used INTEGER,
    
    -- Para Blog Interés General
    urls_researched JSONB, -- Almacena la lista de URLs como un array JSON
    web_research_options_used JSONB, -- Almacena opciones como search_context_size

    -- Para Blog Caso de Éxito
    pdf_filename_original VARCHAR(255),

    -- Output de la generación
    generated_text_main TEXT NOT NULL, -- Post de LinkedIn o artículo de blog completo
    generated_text_summary TEXT, -- Resumen del caso de éxito del blog
    researched_content_summary TEXT, -- Resumen de la investigación web

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL -- Para borrado lógico
);

-- Tabla para las ETIQUETAS (tags) creadas por los usuarios
CREATE TABLE tags (
    tag_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    tag_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT unique_user_tag_name UNIQUE (user_id, tag_name) -- Cada usuario tiene nombres de etiqueta únicos
);

-- Tabla de UNIÓN para la relación muchos-a-muchos entre generated_content y tags
CREATE TABLE content_tags (
    content_id UUID NOT NULL REFERENCES generated_content(content_id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    PRIMARY KEY (content_id, tag_id) -- Clave primaria compuesta
);

-- Índices para mejorar el rendimiento de las búsquedas comunes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_system_prompt_templates_name ON system_prompt_templates(template_name);
CREATE INDEX idx_system_prompt_templates_module_style ON system_prompt_templates(content_module, article_type, style_key);
CREATE INDEX idx_user_custom_prompts_user_id ON user_custom_prompts(user_id);
CREATE INDEX idx_generated_content_user_id ON generated_content(user_id);
CREATE INDEX idx_generated_content_content_type ON generated_content(content_type);
CREATE INDEX idx_tags_user_id_tag_name ON tags(user_id, tag_name);
CREATE INDEX idx_content_tags_content_id ON content_tags(content_id);
CREATE INDEX idx_content_tags_tag_id ON content_tags(tag_id);

-- (Opcional) Funciones para actualizar automáticamente el campo 'updated_at'
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar el trigger a las tablas que tienen 'updated_at'
CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp_user_preferences
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp_system_prompt_templates
BEFORE UPDATE ON system_prompt_templates
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp_user_custom_prompts
BEFORE UPDATE ON user_custom_prompts
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp_generated_content
BEFORE UPDATE ON generated_content
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Nota: La tabla 'tags' no tiene 'updated_at' en este diseño, pero podría añadirse si se necesita.
-- La tabla 'content_tags' es una tabla de unión y usualmente no necesita 'updated_at'.

COMMENT ON TABLE users IS 'Almacena la información de los usuarios registrados.';
COMMENT ON COLUMN users.email IS 'Dirección de correo electrónico única del usuario, usada para login.';
COMMENT ON TABLE user_preferences IS 'Almacena las preferencias personalizadas de cada usuario.';
COMMENT ON TABLE system_prompt_templates IS 'Almacena las plantillas de system prompt base definidas globalmente.';
COMMENT ON COLUMN system_prompt_templates.style_key IS 'Clave de estilo usada por el frontend para identificar la plantilla (ej: leadership, default).';
COMMENT ON TABLE user_custom_prompts IS 'Almacena los system prompts personalizados guardados por cada usuario.';
COMMENT ON COLUMN user_custom_prompts.prompt_name IS 'Nombre que el usuario asigna a su plantilla personalizada.';
COMMENT ON TABLE generated_content IS 'Historial de todo el contenido generado por los usuarios.';
COMMENT ON COLUMN generated_content.custom_title IS 'Título opcional que el usuario puede dar al contenido guardado.';
COMMENT ON COLUMN generated_content.urls_researched IS 'Lista de URLs usadas para investigación en blogs de interés general (formato JSON).';
COMMENT ON TABLE tags IS 'Almacena las etiquetas creadas por los usuarios para organizar su contenido.';
COMMENT ON TABLE content_tags IS 'Tabla de unión para la relación muchos-a-muchos entre contenido generado y etiquetas.';

