import asyncio
import traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.chat_service import responder
from backend.checks import run_all_checks
from backend.scopes import SCOPES

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"resposta": f"Erro interno: {str(exc)}", "fontes": []},
    )


class ChatRequest(BaseModel):
    pergunta: str
    escopo: str = "documentacao"


class ChatResponse(BaseModel):
    resposta: str
    fontes: list


@app.post("/chat")
async def chat(req: ChatRequest):
    result = await asyncio.to_thread(responder, req.pergunta, req.escopo)
    return result


@app.get("/api/checks")
async def checks():
    return await asyncio.to_thread(run_all_checks)


@app.get("/api/scopes")
async def scopes():
    return {
        escopo_id: {
            "label": cfg["label"],
            "icon": cfg["icon"],
        }
        for escopo_id, cfg in SCOPES.items()
    }


frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
