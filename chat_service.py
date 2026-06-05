
import os
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

TERMOS_CRITICOS = ["IA","IU","PF","PJ","UNICLASS","PERSONNALITE"]

embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client_db = chromadb.PersistentClient(path="./db")
collection = client_db.get_collection("knowledge")

client_llm = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

historico = []

def extrair_termos_criticos(pergunta):
    encontrados = []
    pergunta_upper = pergunta.upper()
    for termo in TERMOS_CRITICOS:
        if termo in pergunta_upper:
            encontrados.append(termo)
    return encontrados

def reformular_pergunta(pergunta_atual, historico):
    if len(historico) == 0:
        return pergunta_atual

    conversa = ""
    for item in historico[-5:]:
        conversa += f"Usuário: {item['pergunta']}\\n"
        conversa += f"Assistente: {item['resposta']}\\n\\n"

    prompt = f"""
Sua função é reescrever perguntas curtas utilizando o contexto da conversa.
Retorne SOMENTE a pergunta reescrita.

CONVERSA:
{conversa}

PERGUNTA ATUAL:
{pergunta_atual}
"""

    response = client_llm.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role":"user","content":prompt}],
        temperature=0,
        max_tokens=100
    )

    return response.choices[0].message.content.strip()

def responder(pergunta_original):
    global historico

    pergunta = reformular_pergunta(pergunta_original, historico)

    termos_criticos = extrair_termos_criticos(pergunta)

    pergunta_embedding = embedding_model.encode(pergunta).tolist()

    results = collection.query(
        query_embeddings=[pergunta_embedding],
        n_results=10
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    resultados = []

    for doc, meta, dist in zip(docs, metas, dists):
        score = -dist

        for termo in termos_criticos:
            if termo in doc.upper():
                score += 100

        resultados.append({
            "score": score,
            "doc": doc,
            "meta": meta
        })

    resultados.sort(key=lambda x: x["score"], reverse=True)

    contexto = "\\n\\n".join(
        [r["doc"] for r in resultados[:3]]
    )

    prompt = f"""
Você é um especialista na arquitetura, regras de negócio e processos da squad.

IMPORTANTE:
- Responda SOMENTE usando o contexto fornecido.
- Não invente informações.
- Se não encontrar a resposta no contexto, responda exatamente:
Não encontrei essa informação na documentação disponível.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
"""

    response = client_llm.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role":"user","content":prompt}],
        temperature=0.1,
        max_tokens=1000
    )

    resposta = response.choices[0].message.content

    historico.append({
        "pergunta": pergunta_original,
        "resposta": resposta
    })

    historico = historico[-10:]

    return resposta
