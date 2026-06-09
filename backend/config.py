import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "db"))
DOCS_PATH = os.getenv("DOCS_PATH", str(Path(__file__).resolve().parent.parent / "data" / "docs"))
LLM_MODEL = os.getenv("LLM_MODEL", "meta/llama-3.3-70b-instruct")
LLM_BASE_URL = "https://integrate.api.nvidia.com/v1"
TERMOS_CRITICOS = ["IA", "IU", "PF", "PJ", "UNICLASS", "PERSONNALITE"]

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

AWS_PROFILE = os.getenv("AWS_PROFILE", "")
AWS_REGION = os.getenv("AWS_REGION", "sa-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
AWS_CA_BUNDLE = os.getenv("AWS_CA_BUNDLE", "")
HTTP_PROXY = os.getenv("HTTP_PROXY", "")
HTTPS_PROXY = os.getenv("HTTPS_PROXY", "")
