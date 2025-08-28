# Para usar este endpoint en tu app principal
# app/main.py
from fastapi import FastAPI
from app.api.upload import router as upload_router

app = FastAPI()

app.include_router(upload_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)