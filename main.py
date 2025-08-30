import uvicorn

from app.bootstrap import bootstrap_app


def main() -> None:
    """Punto de entrada principal de la aplicación."""
    app = bootstrap_app()
    uvicorn.run(
        app,
        host="0.0.0.0",  # nosec B104
        port=8000,
        # reload=True
    )


if __name__ == "__main__":
    main()
