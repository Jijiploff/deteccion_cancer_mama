"""
Validaciones de seguridad para los archivos que sube el usuario.
"""
import os
from fastapi import UploadFile, HTTPException, status

from app.config import settings


async def validate_upload_image(file: UploadFile) -> bytes:
    """
    Valida tipo de contenido, extensión y tamaño antes de procesar la imagen.
    Devuelve los bytes ya leídos (para no leer el archivo dos veces).
    """
    # 1. Validar Content-Type declarado por el cliente
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Tipo de archivo no soportado: {file.content_type}. "
                f"Formatos permitidos: JPG, PNG."
            ),
        )

    # 2. Validar extensión del nombre de archivo (defensa adicional, no confiar
    #    solo en content_type porque el cliente puede mentir).
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Extensión de archivo no permitida: {ext}",
        )

    # 3. Leer y validar tamaño real (no confiar en el header Content-Length)
    raw_bytes = await file.read()
    if len(raw_bytes) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo excede el límite de {settings.MAX_FILE_SIZE_MB}MB.",
        )

    if len(raw_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío.",
        )

    return raw_bytes