import os
import socket
from pathlib import Path

from backend.config import CHROMA_DB_PATH


def check_aws():
    try:
        profile = os.getenv("AWS_PROFILE", "N/A")
        region = os.getenv("AWS_REGION", "N/A")
        return {"status": "ok", "data": {"profile": profile, "region": region}}
    except Exception as e:
        return {"status": "fail", "data": {"erro": str(e)}}


def check_onedrive():
    try:
        usuario = os.getlogin()
        onedrive = Path(f"C:\\Users\\{usuario}\\OneDrive")
        if onedrive.exists():
            return {"status": "ok", "data": {"caminho": str(onedrive)}}
        return {"status": "fail", "data": {"caminho": str(onedrive), "motivo": "Pasta nao encontrada"}}
    except Exception as e:
        return {"status": "fail", "data": {"erro": str(e)}}


def check_user():
    try:
        return {
            "status": "ok",
            "data": {
                "usuario": os.getlogin(),
                "computador": os.environ.get("COMPUTERNAME", socket.gethostname()),
            },
        }
    except Exception as e:
        return {"status": "fail", "data": {"erro": str(e)}}


def check_knowledge_base():
    try:
        from backend.kb.client import get_collection
        collection = get_collection()
        count = collection.count()
        return {"status": "ok", "data": {"colecao": "knowledge", "chunks": count}}
    except Exception as e:
        return {"status": "fail", "data": {"erro": str(e), "caminho": CHROMA_DB_PATH}}


def check_ai_services():
    try:
        from backend.config import LLM_PROVIDER, LLM_MODEL, BEDROCK_MODEL_ID
        model = BEDROCK_MODEL_ID if LLM_PROVIDER == "bedrock" else LLM_MODEL
        return {
            "status": "ok",
            "data": {"provider": LLM_PROVIDER, "model": model},
        }
    except Exception as e:
        return {"status": "fail", "data": {"erro": str(e)}}


ALL_CHECKS = [
    {"id": "aws", "label": "AWS Authentication", "fn": check_aws},
    {"id": "onedrive", "label": "OneDrive Access", "fn": check_onedrive},
    {"id": "user", "label": "User Profile", "fn": check_user},
    {"id": "kb", "label": "Knowledge Base", "fn": check_knowledge_base},
    {"id": "ai", "label": "AI Services", "fn": check_ai_services},
]


def run_all_checks():
    resultados = []
    for check in ALL_CHECKS:
        try:
            result = check["fn"]()
            result["id"] = check["id"]
            result["label"] = check["label"]
            resultados.append(result)
        except Exception as e:
            resultados.append({
                "id": check["id"],
                "label": check["label"],
                "status": "fail",
                "data": {"erro": str(e)},
            })
    return resultados
