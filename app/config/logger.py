import logging
import os
import sys
from typing import Any

import structlog


def configure_logging() -> None:
    """Configura el sistema de logging estructurado."""

    # Configurar structlog
    structlog.configure(
        processors=[
            # Agregar timestamp
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            # Agregar información del contexto
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Formatear como JSON en producción, como texto en desarrollo
            structlog.dev.ConsoleRenderer() if _is_development() else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Configurar logging estándar de Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # Configurar niveles específicos
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("ffmpeg").setLevel(logging.WARNING)


def get_logger(name: str) -> Any:
    """
    Obtiene un logger estructurado.

    Args:
        name: Nombre del logger (generalmente __name__)

    Returns:
        Logger estructurado configurado
    """
    return structlog.get_logger(name)


def _is_development() -> bool:
    """Determina si estamos en modo desarrollo."""
    return os.getenv("ENVIRONMENT", "development").lower() == "development"
