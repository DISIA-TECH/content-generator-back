-- postgres-docker/03_permissions.sql
-- Nos aseguramos de operar sobre la base de datos correcta
\c content_generator_db; 

GRANT CONNECT ON DATABASE content_generator_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT CREATE ON SCHEMA public TO app_user; -- Para Alembic (si lo usa el backend al inicio)

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE users TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_preferences TO app_user;
GRANT SELECT ON TABLE system_prompt_templates TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE user_custom_prompts TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE generated_content TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tags TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE content_tags TO app_user;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;