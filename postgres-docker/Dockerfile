FROM postgres:16-alpine

COPY 01_init_roles_db.sql /docker-entrypoint-initdb.d/
COPY 02_schema.sql /docker-entrypoint-initdb.d/
COPY 03_permissions.sql /docker-entrypoint-initdb.d/

EXPOSE 5432