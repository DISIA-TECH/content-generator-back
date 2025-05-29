# (extract_content_from_url podría mejorarse o reemplazarse si el LLM de búsqueda maneja URLs directamente)
# (El resto de funciones se mantienen como estaban)

import requests
from typing import List, Optional # Dict, Any ya no se usan aquí
# import json # No se usa
from io import BytesIO
import re
# from pathlib import Path # No se usa
# import tempfile # No se usa directamente save_temp_file
# import os # No se usa directamente clean_temp_file

from PyPDF2 import PdfReader # Corregido el import si era PdfReader
from core.logger import get_logger
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = get_logger("helpers")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        pdf_file = BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_file) # Usar PdfReader
        
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text: # Asegurarse que hay texto antes de añadir
                text += page_text + "\n"
        
        logger.info(f"Texto extraído de PDF con {len(pdf_reader.pages)} páginas.")
        return text.strip() # Quitar saltos de línea extra al final
    except Exception as e:
        logger.error(f"Error al extraer texto del PDF: {str(e)}", exc_info=True)
        raise # Re-lanzar la excepción para que el llamador la maneje


def format_content_for_readability(content: str) -> str:
    content = re.sub(r'\.(?=[A-Z\d])', '. ', content) # Añadido \d para números después de punto
    content = re.sub(r'\s*\n\s*', '\n', content) # Normalizar espacios alrededor de saltos de línea
    content = re.sub(r'\n{3,}', '\n\n', content) # Reducir múltiples saltos de línea a dos
    content = re.sub(r' {2,}', ' ', content) # Reducir múltiples espacios a uno
    return content.strip()


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False, # Añadido para claridad, default es False
    )
    # create_documents espera una lista de textos, aunque aquí solo sea uno.
    # documents = text_splitter.create_documents([text])
    # return [doc.page_content for doc in documents]
    # O más simple si solo es un texto:
    return text_splitter.split_text(text)


def extract_content_from_url(url: str, timeout: int = 10) -> Optional[str]:
    """Extrae y limpia el contenido de texto de una URL."""
    try:
        headers = { # Añadir User-Agent para evitar bloqueos simples
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status() # Lanza HTTPError para malos responses (4xx o 5xx)
        
        # Intentar decodificar con UTF-8, luego con la detección de requests si falla
        try:
            content = response.content.decode('utf-8')
        except UnicodeDecodeError:
            content = response.text # requests intenta adivinar la codificación

        # Placeholder para una extracción de contenido más sofisticada (ej. usando BeautifulSoup)
        # Por ahora, una limpieza muy básica de HTML y normalización de espacios.
        # Esta parte es la más propensa a necesitar mejoras para contenido web real.
        from bs4 import BeautifulSoup # Importar aquí para no hacerla dependencia dura si no se usa siempre
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extraer texto de etiquetas comunes de contenido
        text_parts = []
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'article', 'section']):
            text_parts.append(tag.get_text(separator=' ', strip=True))
        
        clean_text = ' '.join(text_parts)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip() # Normalizar espacios
        
        if not clean_text: # Si BeautifulSoup no extrajo mucho, intentar con regex como fallback (menos ideal)
            logger.warning(f"BeautifulSoup extrajo poco texto de {url}, intentando regex fallback.")
            clean_text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            clean_text = re.sub(r'<style[^>]*>.*?</style>', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
            clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        logger.info(f"Contenido extraído (longitud: {len(clean_text)}) de URL: {url}")
        return clean_text if clean_text else None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red al extraer contenido de URL {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Error general al extraer contenido de URL {url}: {str(e)}", exc_info=True)
    return None


def extract_hashtags(text: str) -> List[str]:
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags