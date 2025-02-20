from fastapi import FastAPI
from app.api.routes import rag, board, doc
from dotenv import load_dotenv
import os

from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="API IAKATA")

API_WEB = os.getenv("WEB_API_BASE_URL")

app.include_router(board.router, prefix="/board", tags=["BOARD"])
app.include_router(rag.router, prefix="/chatbot", tags=["RAG"])
app.include_router(doc.router, prefix="/doc", tags=["DOC"])

@app.get("/")
def root():
    return {"message": "API - LEANKATA"}