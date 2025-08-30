import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.adapters import ffmpeg_audio_extraction_adapter
from app.adapters import openai_transcription_adapter
from app.config.logger import configure_logging, get_logger
from app.entrypoints import fastapi_app
from app.service import manager

logger = get_logger(__name__)


def bootstrap_app() -> FastAPI:
    """
    Configura e inicializa la aplicación con todas las dependencias.

    Returns:
        Aplicación FastAPI configurada con dependencias inyectadas
    """
    logger.info("Iniciando bootstrap de la aplicación")

    # Configurar logging
    configure_logging()
    logger.info("Sistema de logging configurado")

    # Cargar variables de entorno
    load_dotenv()
    logger.info("Variables de entorno cargadas")

    # Obtener API key de OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY no está configurada en las variables de entorno")
        raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")

    logger.info("API key de OpenAI configurada correctamente")

    # Crear adapter de extracción de audio
    logger.info("Creando adapter de extracción de audio")
    audio_extraction_adapter = ffmpeg_audio_extraction_adapter.FFmpegAudioExtractionAdapter()

    # Crear adapter de transcripción con extracción de audio inyectada
    logger.info("Creando adapter de transcripción OpenAI")
    transcription_adapter = openai_transcription_adapter.OpenAITranscriptionAdapter(
        api_key=openai_api_key, audio_extraction_service=audio_extraction_adapter
    )

    # Crear service manager con dependencias inyectadas
    logger.info("Creando service manager")
    service_manager = manager.ServiceManager(transcription_service=transcription_adapter)

    # Crear y retornar la aplicación FastAPI
    logger.info("Creando aplicación FastAPI")
    app = fastapi_app.create_app(service_manager)

    logger.info("Bootstrap completado exitosamente")
    return app
