from fastapi import UploadFile
from openai import OpenAI

from app import ports
from app.config.logger import get_logger

logger = get_logger(__name__)


class OpenAITranscriptionAdapter(ports.TranscriptionService):
    """Adapter para el servicio de transcripción usando OpenAI."""

    def __init__(self, api_key: str | None = None, audio_extraction_service: ports.AudioExtractionService | None = None) -> None:
        """
        Inicializa el adapter de OpenAI.

        Args:
            api_key: API key de OpenAI. Si no se proporciona, se usa la variable de entorno.
            audio_extraction_service: Servicio de extracción de audio inyectado
        """
        self._client = OpenAI(api_key=api_key)
        self._audio_extraction_service = audio_extraction_service

        logger.info("OpenAI adapter inicializado", has_audio_extraction_service=audio_extraction_service is not None)

    async def transcribe_from_upload(self, uploaded_file: UploadFile, model: str = "whisper-1") -> str:
        """
        Transcribe un archivo subido usando OpenAI Whisper.

        Args:
            uploaded_file: Archivo subido por el usuario
            model: Modelo a utilizar (por defecto whisper-1)

        Returns:
            Texto transcrito del audio
        """
        logger.info(
            "Iniciando transcripción con OpenAI",
            filename=uploaded_file.filename,
            model=model,
            has_extraction_service=self._audio_extraction_service is not None,
        )

        try:
            # Extraer audio si es necesario (solo si se inyectó el servicio)
            if self._audio_extraction_service:
                logger.info("Extrayendo audio del archivo", filename=uploaded_file.filename)
                audio_stream, filename = await self._audio_extraction_service.extract_audio_stream(uploaded_file)
                logger.info("Audio extraído exitosamente", extracted_filename=filename)
            else:
                # Fallback: usar el archivo directamente
                logger.info("Usando archivo directamente sin extracción", filename=uploaded_file.filename)
                await uploaded_file.seek(0)
                audio_stream, filename = uploaded_file.file, uploaded_file.filename or "audio"

            # Transcribir con OpenAI
            logger.info("Enviando archivo a OpenAI para transcripción", filename=filename, model=model)
            transcription = self._client.audio.transcriptions.create(model=model, file=(filename, audio_stream), response_format="text")

            logger.info("Transcripción de OpenAI completada", filename=filename, model=model, transcription_length=len(transcription))

            return str(transcription)

        except Exception as e:
            logger.error("Error en transcripción de OpenAI", filename=uploaded_file.filename, model=model, error=str(e), exc_info=True)
            raise
