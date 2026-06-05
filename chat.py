import os
import chromadb

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI


# ============================================================
# CONFIGURAÇÕES
# ============================================================

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

TERMOS_CRITICOS = [
    "IA",
    "IU",
    "PF",
    "PJ",
    "UNICLASS",
    "PERSONNALITE"
]


# ============================================================
# FUNÇÕES
# ============================================================

def extrair_termos_criticos(pergunta):

    encontrados = []

    pergunta_upper = pergunta.upper()

    for termo in TERMOS_CRITICOS:

        if termo in pergunta_upper:
            encontrados.append(termo)

    return encontrados


# ============================================================
# MODELO DE EMBEDDINGS
# ============================================================

print("Carregando modelo de embeddings...")

embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Modelo carregado.")


# ============================================================
# CHROMADB
# ============================================================

client_db = chromadb.PersistentClient(
    path="./db"
)

collection = client_db.get_collection(
    "knowledge"
)


# ============================================================
# NVIDIA
# ============================================================

client_llm = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

historico = []

# ============================================================
# REESCREVE PERGUNTA
# ============================================================
def reformular_pergunta(
    pergunta_atual,
    historico,
    client_llm
):

    if len(historico) == 0:
        return pergunta_atual

    conversa = ""

    for item in historico[-5:]:

        conversa += (
            f"Usuário: {item['pergunta']}\n"
        )

        conversa += (
            f"Assistente: {item['resposta']}\n\n"
        )

    prompt = f"""
                    Sua função é reescrever perguntas curtas
                    utilizando o contexto da conversa.

                    Exemplos:

                    Pergunta:
                    "E para o IA?"

                    Resposta:
                    "Qual a regra do cadastro de órgão para o segmento IA?"

                    Pergunta:
                    "Qual tabela?"

                    Resposta:
                    "Qual tabela contém as novas agências?"

                    Retorne SOMENTE a pergunta reescrita.

                    CONVERSA:

                    {conversa}

                    PERGUNTA ATUAL:

                    {pergunta_atual}
                    """

    response = client_llm.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=100
    )

    return (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    pergunta = input("\nPergunta: ")

    pergunta_original = pergunta

    pergunta = reformular_pergunta(
        pergunta,
        historico,
        client_llm
    )

    print(
        f"\nPergunta interpretada: {pergunta}"
    )

    if pergunta.lower() in ["sair", "exit", "quit"]:
        break

    print("\nBuscando conhecimento...")

    termos_criticos = extrair_termos_criticos(
        pergunta
    )

    pergunta_embedding = embedding_model.encode(
        pergunta
    ).tolist()

    results = collection.query(
        query_embeddings=[pergunta_embedding],
        n_results=10
    )

    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    resultados = []

    for doc, meta, dist in zip(
        docs,
        metadatas,
        distances
    ):

        score = -dist

        texto_upper = doc.upper()

        bonus = 0

        for termo in termos_criticos:

            if termo in texto_upper:
                bonus += 100

        score += bonus

        resultados.append(
            {
                "score": score,
                "bonus": bonus,
                "dist": dist,
                "doc": doc,
                "meta": meta
            }
        )

    resultados.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # ========================================================
    # MONTA CONTEXTO
    # ========================================================

    contexto = ""

    fontes = set()

    for r in resultados[:3]:

        contexto += r["doc"]
        contexto += "\n\n"

        fontes.add(
            r["meta"]["source"]
        )

    # ========================================================
    # PROMPT
    # ========================================================

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

    print("\nConsultando modelo...\n")

    response = client_llm.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=1000
    )

    resposta = response.choices[0].message.content

    historico.append(
        {
            "pergunta": pergunta_original,
            "resposta": resposta
        }
    )

    historico = historico[-10:]

    # ========================================================
    # SAÍDA
    # ========================================================

    print("\n")
    print("=" * 100)
    print("RESPOSTA")
    print("=" * 100)

    print(resposta)

    print("\n")
    print("=" * 100)
    print("FONTES")
    print("=" * 100)

    for fonte in fontes:
        print(f"- {fonte}")

    print("\n")