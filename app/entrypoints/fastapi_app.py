from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.config.logger import get_logger
from app.entrypoints import dtos
from app.service import manager

logger = get_logger(__name__)


def create_app(service_manager: manager.ServiceManager) -> FastAPI:
    """
    Crea la aplicación FastAPI con las dependencias inyectadas.

    Args:
        service_manager: Gestor de servicios inyectado

    Returns:
        Aplicación FastAPI configurada
    """
    logger.info("Creando aplicación FastAPI")

    app = FastAPI(
        title="Video Transcriber API", description="API para transcribir archivos de audio y video usando OpenAI Whisper", version="1.0.0"
    )

    logger.info("Aplicación FastAPI creada exitosamente")

    def get_service_manager() -> manager.ServiceManager:
        """Dependency provider para el ServiceManager."""
        return service_manager

    @app.post(
        "/transcribe",
        response_model=dtos.TranscriptionResponse,
        responses={400: {"model": dtos.ErrorResponse}, 500: {"model": dtos.ErrorResponse}},
    )
    async def transcribe_media(
        file: Annotated[UploadFile, File(description="Archivo de audio o video a transcribir")],
        model: Annotated[str, Form(description="Modelo de OpenAI a utilizar")] = "whisper-1",
        service_manager: manager.ServiceManager = Depends(get_service_manager),
    ) -> dtos.TranscriptionResponse | JSONResponse:
        """
        Transcribe un archivo de audio o video a texto.

        Args:
            file: Archivo de audio/video subido
            model: Modelo de OpenAI a utilizar
            service_manager: Gestor de servicios inyectado

        Returns:
            Respuesta con la transcripción o error
        """
        logger.info(
            "Recibida solicitud de transcripción", filename=file.filename, content_type=file.content_type, model=model, file_size=file.size
        )

        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith(("audio/", "video/")):
            logger.warning("Archivo rechazado por tipo de contenido inválido", filename=file.filename, content_type=file.content_type)
            return {"msg": "El archivo debe ser de tipo audio o video"}, 400

        try:
            # Transcribir directamente desde el archivo subido
            transcription = await service_manager.transcribe_media(uploaded_file=file, model=model)

            logger.info(
                "Solicitud de transcripción completada exitosamente",
                filename=file.filename,
                model=model,
                transcription_length=len(transcription),
            )

            return dtos.TranscriptionResponse(transcription=transcription)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error procesando solicitud de transcripción", filename=file.filename, model=model, error=str(e), exc_info=True)
            return JSONResponse(status_code=500, content=dtos.ErrorResponse(error="Error interno del servidor").model_dump())

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Endpoint de health check."""
        logger.debug("Health check solicitado")
        return {"status": "healthy"}

    logger.info("Configuración de endpoints completada")
    return app
