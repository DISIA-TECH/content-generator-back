# (Nuevo archivo para configurar SQLAlchemy)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# El argumento connect_args es específico para SQLite, no necesario para PostgreSQL por defecto.
# Si necesitas configuraciones específicas para el pool de PostgreSQL, se pueden añadir aquí.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener una sesión de base de datos en los endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()