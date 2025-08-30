import tempfile
import os
from typing import BinaryIO
from pathlib import Path
from io import BytesIO

import ffmpeg
from fastapi import UploadFile

from app import ports
from app.config.logger import get_logger

logger = get_logger(__name__)


class FFmpegAudioExtractionAdapter(ports.AudioExtractionService):
    """Adapter para extraer audio usando FFmpeg."""

    def __init__(self) -> None:
        """Inicializa el adapter de FFmpeg."""
        logger.info("FFmpeg audio extraction adapter inicializado")

    async def extract_audio_stream(self, uploaded_file: UploadFile) -> tuple[BinaryIO, str]:
        """
        Extrae audio de un archivo de video/audio y retorna un stream.

        Args:
            uploaded_file: Archivo subido por el usuario

        Returns:
            Tupla con (stream_de_audio, nombre_archivo)
        """
        file_extension = Path(uploaded_file.filename or "").suffix.lower()

        logger.info(
            "Analizando archivo para extracción de audio",
            filename=uploaded_file.filename,
            file_extension=file_extension,
            file_size=uploaded_file.size,
        )

        # Si ya es un formato de audio soportado por Whisper, pasarlo directamente
        if file_extension in [".mp3", ".wav", ".m4a", ".flac", ".ogg"]:
            logger.info(
                "Archivo ya está en formato de audio soportado, usando directamente",
                filename=uploaded_file.filename,
                file_extension=file_extension,
            )
            await uploaded_file.seek(0)  # Asegurar que estamos al inicio
            return uploaded_file.file, uploaded_file.filename or "audio"

        # Para videos o formatos no soportados, extraer audio
        logger.info("Archivo requiere extracción de audio", filename=uploaded_file.filename, file_extension=file_extension)
        return await self._extract_audio_with_ffmpeg(uploaded_file)

    async def _extract_audio_with_ffmpeg(self, uploaded_file: UploadFile) -> tuple[BinaryIO, str]:
        """Extrae audio usando ffmpeg."""
        logger.info("Iniciando extracción de audio con FFmpeg", filename=uploaded_file.filename)

        # Crear archivos temporales
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.filename or "").suffix) as input_temp:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as output_temp:
                try:
                    logger.info("Creando archivos temporales para extracción", input_temp=input_temp.name, output_temp=output_temp.name)

                    # Escribir archivo de entrada
                    content = await uploaded_file.read()
                    input_temp.write(content)
                    input_temp.flush()

                    logger.info("Archivo temporal de entrada creado", input_size=len(content), input_file=input_temp.name)

                    # Extraer audio con ffmpeg
                    logger.info("Ejecutando FFmpeg para extracción de audio")
                    try:
                        (
                            ffmpeg.input(input_temp.name)
                            .output(output_temp.name, acodec="mp3", audio_bitrate="128k")
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True)
                        )
                    except ffmpeg.Error as e:
                        # Capturar stderr para ver el error específico
                        stderr_output = e.stderr.decode("utf-8", errors="replace") if e.stderr else "No stderr available"
                        logger.error("FFmpeg falló con error específico", filename=uploaded_file.filename, stderr=stderr_output)
                        raise

                    # Leer el archivo de audio extraído
                    with open(output_temp.name, "rb") as audio_file:
                        audio_content = audio_file.read()

                    logger.info("Audio extraído exitosamente", output_size=len(audio_content), output_file=output_temp.name)

                    # Crear stream en memoria
                    audio_stream = BytesIO(audio_content)
                    audio_filename = f"{Path(uploaded_file.filename or 'audio').stem}.mp3"

                    logger.info("Stream de audio creado", audio_filename=audio_filename, stream_size=len(audio_content))

                    return audio_stream, audio_filename

                except Exception as e:
                    logger.error(
                        "Error durante extracción de audio con FFmpeg", filename=uploaded_file.filename, error=str(e), exc_info=True
                    )
                    raise

                finally:
                    # Limpiar archivos temporales
                    logger.debug("Limpiando archivos temporales")
                    os.unlink(input_temp.name)
                    os.unlink(output_temp.name)
                    logger.debug("Archivos temporales eliminados exitosamente")
