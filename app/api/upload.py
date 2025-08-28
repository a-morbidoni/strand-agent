from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from pathlib import Path
import uuid

from orchestrator import procesar_imagen_telegram

router = APIRouter(prefix="/upload", tags=["upload"])

# Crear carpeta de uploads si no existe
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Recibe un archivo del frontend y lo guarda en la carpeta uploads
    """
    try:
        # Generar nombre único para evitar conflictos
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Leer contenido del archivo
        content = await file.read()
        
        # Guardar archivo en la carpeta
        with open(file_path, "wb") as f:
            f.write(content)

          # Procesar imagen automáticamente
        processing_success = procesar_imagen_telegram(str(file_path))

        return {
            "message": "Archivo subido exitosamente",
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_size": len(content),
            "file_path": str(file_path),
            "processing_status": "success" if processing_success else "error"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo: {str(e)}")

