from abc import ABC, abstractmethod
from typing import BinaryIO

from fastapi import UploadFile


class TranscriptionService(ABC):
    """Puerto para el servicio de transcripción de audio/video."""

    @abstractmethod
    async def transcribe_from_upload(self, uploaded_file: UploadFile, model: str = "whisper-1") -> str:
        """
        Transcribe un archivo subido (audio o video) a texto.

        Args:
            uploaded_file: Archivo subido por el usuario
            model: Modelo a utilizar para la transcripción

        Returns:
            Texto transcrito del archivo
        """
        raise NotImplementedError


class AudioExtractionService(ABC):
    """Puerto para el servicio de extracción de audio."""

    @abstractmethod
    async def extract_audio_stream(self, uploaded_file: UploadFile) -> tuple[BinaryIO, str]:
        """
        Extrae audio de un archivo de video/audio y retorna un stream.

        Args:
            uploaded_file: Archivo subido por el usuario

        Returns:
            Tupla con (stream_de_audio, nombre_archivo)
        """
        raise NotImplementedError
