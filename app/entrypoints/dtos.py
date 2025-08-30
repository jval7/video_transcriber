from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """DTO para la solicitud de transcripción."""

    model: str = Field(default="whisper-1", description="Modelo de OpenAI a utilizar para la transcripción")


class TranscriptionResponse(BaseModel):
    """DTO para la respuesta de transcripción."""

    transcription: str = Field(description="Texto transcrito del archivo de audio/video")
    success: bool = Field(default=True, description="Indica si la transcripción fue exitosa")


class ErrorResponse(BaseModel):
    """DTO para respuestas de error."""

    success: bool = Field(default=False, description="Indica que ocurrió un error")
    error: str = Field(description="Mensaje de error")
