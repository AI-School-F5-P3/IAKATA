from fastapi import FastAPI
from app.api.routes import rag, board, doc, chat
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="API IAKATA")

# Configuración de CORS
origins = [
    "http://localhost:3000",  # Frontend en puerto 3000
    "http://localhost:5173",  # Puerto por defecto de Vite
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    # Añade aquí otros orígenes necesarios
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)


API_WEB = os.getenv("WEB_API_BASE_URL")

app.include_router(board.router, prefix="/board", tags=["BOARD"])
app.include_router(rag.router, prefix="/chatbot", tags=["RAG"])
app.include_router(doc.router, prefix="/doc", tags=["DOC"])
app.include_router(chat.router, prefix="/chat", tags=["CHAT"]) 

@app.get("/")
def root():
    return {"message": "API - LEANKATA"}