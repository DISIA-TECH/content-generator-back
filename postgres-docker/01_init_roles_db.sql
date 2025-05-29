-- postgres-docker/01_init_roles_db.sql
-- El rol app_owner y la base de datos content_generator_db 
-- son creados por las variables de entorno POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB.

-- Solo necesitamos crear app_user si no existe.
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
      CREATE ROLE app_user LOGIN PASSWORD '123456';
   END IF;
END
$$;