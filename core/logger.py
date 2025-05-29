import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from core.config import settings

# Crear directorio de logs si no existe
os.makedirs("logs", exist_ok=True)


def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Configura y devuelve un logger con el nombre especificado.

    Args:
        name (str): El nombre del logger.
        log_level (Optional[str]): El nivel de log a utilizar, por defecto usa el de settings.

    Returns:
        logging.Logger: El logger configurado.
    """
    level = getattr(logging, log_level or settings.LOG_LEVEL)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato de logs
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(level)
    
    # Handler para archivo rotativo (10 MB máximo por archivo, guarda hasta 5 archivos)
    file_handler = RotatingFileHandler(
        filename=f"logs/{name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(level)
    
    # Agregar handlers al logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Logger principal de la aplicación
app_logger = get_logger("content_generator")