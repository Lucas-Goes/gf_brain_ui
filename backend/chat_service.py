import chromadb
from sentence_transformers import SentenceTransformer

from backend.config import (
    NVIDIA_API_KEY, CHROMA_DB_PATH, LLM_MODEL, LLM_BASE_URL, TERMOS_CRITICOS,
    LLM_PROVIDER, AWS_PROFILE, AWS_REGION, BEDROCK_MODEL_ID, AWS_CA_BUNDLE,
    HTTP_PROXY, HTTPS_PROXY,
)
from backend.llm_provider import create_provider

STOP_WORDS = {
    "qual", "a", "o", "as", "os", "e", "de", "da", "do", "das", "dos",
    "para", "com", "em", "no", "na", "nos", "nas", "um", "uma", "umas",
    "uns", "que", "é", "são", "tem", "como", "por", "pra", "pro", "num",
    "pelo", "pela", "aos", "ao", "se", "sua", "seu", "suas", "seus",
    "ele", "ela", "voce", "nós", "vos", "mais", "mas", "ja", "já",
    "sim", "nao", "não", "ser", "esta", "está", "estão", "era", "só",
    "so", "ate", "até", "vai", "vão", "sem", "entre", "depois", "antes",
    "sob", "sobre", "quando", "onde", "porque", "pois", "sendo", "tendo",
    "ter", "nenhum", "todas", "todos", "cada", "qualquer", "mesmo",
    "outro", "outra", "algum", "alguma", "muito", "pouco", "bastante",
    "demais", "tanto", "quanto", "varios", "vários", "diversos",
    "principais", "principal", "apenas", "somente", "cerca", "quase",
}


def _extrair_palavras_chave(texto):
    palavras = set()
    for p in texto.lower().split():
        p = p.strip(".,;:!?\"'()[]{}/\\-_")
        if len(p) > 2 and p not in STOP_WORDS:
            palavras.add(p)
    return palavras

embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client_db = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client_db.get_collection("knowledge")

llm = create_provider({
    "LLM_PROVIDER": LLM_PROVIDER,
    "NVIDIA_API_KEY": NVIDIA_API_KEY,
    "LLM_BASE_URL": LLM_BASE_URL,
    "LLM_MODEL": LLM_MODEL,
    "AWS_PROFILE": AWS_PROFILE,
    "AWS_REGION": AWS_REGION,
    "BEDROCK_MODEL_ID": BEDROCK_MODEL_ID,
})

historico = []

SEPARADOR = "=" * 100


def extrair_termos_criticos(pergunta):
    encontrados = []
    pergunta_upper = pergunta.upper()
    for termo in TERMOS_CRITICOS:
        if termo in pergunta_upper:
            encontrados.append(termo)
    return encontrados


def reformular_pergunta(pergunta_atual, historico):
    if len(historico) == 0:
        print(f"[REFORMULAR] Historico vazio -> pergunta original mantida")
        return pergunta_atual

    conversa = ""
    for item in historico[-5:]:
        conversa += f"Usuário: {item['pergunta']}\n"
        conversa += f"Assistente: {item['resposta']}\n\n"

    prompt = f"""
Sua função é reescrever perguntas curtas utilizando o contexto da conversa.

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

    print(f"[REFORMULAR] Pergunta original: {pergunta_atual}")
    reformulada = llm.generate(prompt=prompt, temperature=0, max_tokens=100)
    print(f"[REFORMULAR] Pergunta interpretada: {reformulada}")
    return reformulada


def responder(pergunta_original):
    global historico

    print(f"\n{SEPARADOR}")
    print(f"CHAT INICIADO")
    print(f"{SEPARADOR}")
    print(f"Pergunta original: {pergunta_original}")

    pergunta = reformular_pergunta(pergunta_original, historico)

    print(f"\n[TERMOS] Buscando termos criticos...")
    termos_criticos = extrair_termos_criticos(pergunta)
    if termos_criticos:
        print(f"[TERMOS] Encontrados: {termos_criticos}")
    else:
        print(f"[TERMOS] Nenhum termo critico encontrado")

    print(f"\n[EMBEDDING] Gerando embedding da pergunta...")
    pergunta_embedding = embedding_model.encode(pergunta).tolist()

    print(f"[CHROMA] Consultando base de conhecimento...")
    results = collection.query(
        query_embeddings=[pergunta_embedding],
        n_results=10
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    print(f"[CHROMA] Recuperados {len(docs)} documentos")

    palavras_pergunta = _extrair_palavras_chave(pergunta)
    palavras_pergunta -= {t.lower() for t in termos_criticos}

    resultados = []

    for doc, meta, dist in zip(docs, metas, dists):
        score = -dist
        bonus = 0
        bonus_detalhes = []

        for termo in termos_criticos:
            count = doc.upper().count(termo)
            if count > 0:
                pts = min(count * 30, 150)
                bonus += pts
                bonus_detalhes.append(f"{termo}x{count}={pts}")

        doc_lower = doc.lower()
        palavras_no_chunk = {p for p in palavras_pergunta if p in doc_lower}
        if palavras_no_chunk:
            pts = min(len(palavras_no_chunk) * 15, 90)
            bonus += pts
            bonus_detalhes.append(f"kw{len(palavras_no_chunk)}={pts}")

        score += bonus
        resultados.append({
            "score": score,
            "bonus": bonus,
            "bonus_detalhes": "+".join(bonus_detalhes) if bonus_detalhes else "0",
            "dist": dist,
            "doc": doc,
            "meta": meta
        })

    resultados.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n[SCORE] Resultados ranqueados (top 5):")
    for r in resultados[:5]:
        print(f"  score={r['score']:.2f} | bonus={r['bonus']} ({r['bonus_detalhes']}) | dist={r['dist']:.2f} | fonte={r['meta']['source']} | chunk={r['meta'].get('chunk', '?')}")

    contexto = ""
    fontes = set()

    for r in resultados[:3]:
        contexto += r["doc"] + "\n\n"
        fontes.add(r["meta"]["source"])

    print(f"\n[CONTEXTO] Usando {len(resultados[:3])} documentos:")
    for f in fontes:
        print(f"  - {f}")

    prompt = f"""
Contexto extraido da base de conhecimento:
{contexto}

Com base no contexto acima, responda a pergunta abaixo.
Se o contexto nao contiver a resposta, escreva exatamente:
Nao encontrei essa informacao na documentacao disponivel.

PERGUNTA: {pergunta}

RESPOSTA:"""

    print(f"\n[LLM] Consultando {LLM_PROVIDER}...")
    try:
        resposta = llm.generate(prompt=prompt, temperature=0.0, max_tokens=500)
        print(f"[LLM] Resposta recebida ({len(resposta)} caracteres)")
    except Exception as e:
        resposta = f"Erro ao consultar a IA: {str(e)}"
        print(f"[LLM] ERRO: {e}")

    historico.append({
        "pergunta": pergunta_original,
        "resposta": resposta
    })

    historico = historico[-10:]

    print(f"\n[FONTES] Documentos utilizados:")
    for f in fontes:
        print(f"  - {f}")
    print(f"{SEPARADOR}\n")

    return {"resposta": resposta, "fontes": list(fontes)}
