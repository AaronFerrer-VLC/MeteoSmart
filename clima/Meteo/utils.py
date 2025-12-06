"""
Utility functions for the Meteo application.

This module provides helper functions for database connections,
API interactions, and common operations.
"""
import os
import logging
import cx_Oracle
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@contextmanager
def get_oracle_connection():
    """
    Context manager for Oracle database connections.
    
    Ensures proper connection handling and cleanup.
    
    Yields:
        cx_Oracle.Connection: Oracle database connection
        
    Raises:
        ValueError: If required environment variables are missing
        cx_Oracle.DatabaseError: If connection fails
    """
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")
    
    if not all([user, password, dsn]):
        error_msg = "Faltan variables de entorno para la conexión a Oracle."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    conn = None
    try:
        conn = cx_Oracle.connect(user, password, dsn)
        logger.debug("Conexión a Oracle establecida correctamente")
        yield conn
    except cx_Oracle.DatabaseError as e:
        logger.error(f"Error de base de datos Oracle: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado en conexión Oracle: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Conexión a Oracle cerrada")


def validate_city_name(city_name: str) -> bool:
    """
    Validate city name format.
    
    Args:
        city_name: Name of the city to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not city_name or not isinstance(city_name, str):
        return False
    
    # Remove leading/trailing whitespace
    city_name = city_name.strip()
    
    # Check length
    if len(city_name) < 2 or len(city_name) > 100:
        return False
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not all(c.isalpha() or c.isspace() or c in ("-", "'", "á", "é", "í", "ó", "ú", "ñ", "ü") 
               for c in city_name.lower()):
        return False
    
    return True

