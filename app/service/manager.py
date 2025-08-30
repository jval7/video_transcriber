from fastapi import UploadFile

from app import ports
from app.config.logger import get_logger

logger = get_logger(__name__)


class ServiceManager:
    """Gestor de servicios para el procesamiento de medios."""

    def __init__(self, transcription_service: ports.TranscriptionService) -> None:
        """
        Inicializa el gestor de servicios.

        Args:
            transcription_service: Servicio de transcripción inyectado
        """
        self._transcription_service = transcription_service
        logger.info("ServiceManager inicializado correctamente")

    async def transcribe_media(self, uploaded_file: UploadFile, model: str = "whisper-1") -> str:
        """
        Procesa un archivo de media para transcribirlo a texto.

        Args:
            uploaded_file: Archivo subido por el usuario
            model: Modelo a utilizar para la transcripción

        Returns:
            Texto transcrito del archivo
        """
        logger.info(
            "Iniciando transcripción de archivo",
            filename=uploaded_file.filename,
            content_type=uploaded_file.content_type,
            model=model,
            file_size=uploaded_file.size,
        )

        result = await self._transcription_service.transcribe_from_upload(uploaded_file=uploaded_file, model=model)

        logger.info("Transcripción completada exitosamente", filename=uploaded_file.filename, model=model, transcription_length=len(result))

        return result
