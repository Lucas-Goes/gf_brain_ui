from backend.agent.prompts import get_system_prompt, get_tools_for_scope, get_kb_filter
from backend.kb.client import query_knowledge
from backend.tools.base import Tool


def executar(pergunta, escopo, llm):
    system_prompt = get_system_prompt(escopo)
    kb_filter = get_kb_filter(escopo)

    results = query_knowledge(pergunta, n_results=10, where_filter=kb_filter)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    contexto = "\n\n".join(docs[:3])
    fontes = set()
    for meta in metas[:3]:
        fontes.add(meta.get("source", "desconhecido"))

    prompt = f"""Contexto extraido da base de conhecimento:
{contexto}

Com base no contexto acima, responda a pergunta abaixo.
Se o contexto nao contiver a resposta, escreva exatamente:
Nao encontrei essa informacao na documentacao disponivel.

PERGUNTA: {pergunta}

RESPOSTA:"""

    resposta = llm.generate(
        prompt=prompt,
        temperature=0.0,
        max_tokens=500,
        system_prompt=system_prompt,
    )

    return {
        "resposta": resposta,
        "fontes": list(fontes),
    }
