"""
Logging centralizado. En Render, los logs a stdout se capturan automáticamente
en el dashboard, así que no escribimos a archivo por defecto (evita problemas
con filesystems efímeros). Si corres localmente y quieres archivo, ajusta
LOG_TO_FILE.
"""
import logging
import sys
from app.config import settings


def setup_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    # Bajar verbosidad de librerías ruidosas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)