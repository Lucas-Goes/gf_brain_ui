from backend.config import (
    NVIDIA_API_KEY, LLM_MODEL, LLM_BASE_URL, TERMOS_CRITICOS,
    LLM_PROVIDER, AWS_PROFILE, AWS_REGION, BEDROCK_MODEL_ID,
)
from backend.llm_provider import create_provider
from backend.kb.client import query_knowledge as kb_query
from backend.agent.prompts import get_system_prompt, get_kb_filter

SAUDACOES = [
    "oi", "ola", "olá", "oie", "ooi", "bom dia", "boa tarde", "boa noite",
    "opa", "fala", "falae", "e aí", "eai", "hey", "hello", "hi",
]
CAPABILITIES = [
    "o que voce sabe", "o que voce faz", "o que voce pode",
    "quem é voce", "quem e voce", "como funciona",
    "me ajuda", "pode me ajudar", "sabe fazer", "consegue fazer",
    "o que sabe", "capacidades", "habilidades",
]
AGRADECIMENTOS = [
    "obrigado", "obrigada", "valeu", "brigado", "brigada",
    "thanks", "thank you", "valeu", "tmj",
]

SCOPE_INTRO_RESPONSES = {
    "codigo": (
        "Sou o **GF Brain** no modo **Criar Código**\\. Posso analisar os padrões do projeto "
        "e sugerir implementações de Glue jobs, tabelas Athena, pipelines e muito mais\\.\n\n"
        "**Exemplos do que posso fazer:**\n"
        "• Sugerir a estrutura de um job Glue seguindo os padrões do projeto\n"
        "• Indicar colunas importantes para tabelas (dt\\_foto, id\\_segmento, etc\\.)\n"
        "• Gerar código com logging e conceito Athena First\n"
        "• Revisar código existente e apontar melhorias\n\n"
        "Sobre o que você gostaria de criar?"
    ),
    "arquitetura": (
        "Sou o **GF Brain** no modo **Analisar Arquitetura**\\. Posso analisar a arquitetura "
        "dos processos e fluxos de dados com base nos padrões documentados do projeto\\.\n\n"
        "**Exemplos do que posso fazer:**\n"
        "• Explicar o fluxo completo de cadastro de clientes/agências/órgãos\n"
        "• Detalhar a arquitetura de processamento dos segmentos (PF/PJ)\n"
        "• Analisar dependências entre bases e jobs\n"
        "• Sugerir melhorias de escalabilidade e manutenibilidade\n\n"
        "Qual área da arquitetura você quer explorar?"
    ),
    "documentacao": (
        "Sou o **GF Brain** no modo **Documentação**\\. Consulto a base de conhecimento "
        "para responder suas perguntas com o máximo de detalhes e fontes\\.\n\n"
        "**Exemplos do que posso fazer:**\n"
        "• Explicar regras de negócio dos segmentos (IA, IU, PF, PJ, etc\\.)\n"
        "• Detalhar processos de cadastro de órgãos, agências e clientes\n"
        "• Esclarecer dúvidas sobre fluxos e validações\n"
        "• Buscar informações específicas na documentação disponível\n\n"
        "O que você gostaria de saber?"
    ),
    "automacao": (
        "Sou o **GF Brain** no modo **Automações**\\. Posso executar tarefas "
        "no seu computador usando as ferramentas disponíveis\\.\n\n"
        "**Exemplos do que posso fazer:**\n"
        "• Abrir o Notepad e escrever um poema na área de trabalho\n"
        "• Criar arquivos e pastas automatizados\n"
        "• Executar comandos e processos\n\n"
        "O que você quer automatizar?"
    ),
}


ACENTOS = str.maketrans({
    "á": "a", "à": "a", "â": "a", "ã": "a",
    "é": "e", "ê": "e",
    "í": "i",
    "ó": "o", "ô": "o", "õ": "o",
    "ú": "u",
    "ç": "c",
})


def _normalizar(texto):
    return texto.lower().strip().strip(".,;:!?").translate(ACENTOS)


def _detectar_saudacao(texto):
    t = _normalizar(texto)

    for padrao in SAUDACOES:
        if t == padrao or t.startswith(padrao):
            return "saudacao"
        if len(padrao) > 2 and padrao in t:
            return "saudacao"

    for padrao in CAPABILITIES:
        if padrao in t:
            return "capability"

    for padrao in AGRADECIMENTOS:
        if padrao in t:
            return "agradecimento"

    return None


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
_pendente_automacao = None

SEPARADOR = "=" * 100


def extrair_termos_criticos(pergunta):
    encontrados = []
    pergunta_upper = pergunta.upper()
    for termo in TERMOS_CRITICOS:
        if termo in pergunta_upper:
            encontrados.append(termo)
    return encontrados


def _listar_ferramentas_texto(tools_dict):
    if not tools_dict:
        return "Nenhuma ferramenta de automação disponível no momento."
    linhas = []
    for nome, cls in tools_dict.items():
        linhas.append(f"• **{nome}**: {cls.description}")
    return "\n".join(linhas)


def _executar_ferramenta(nome, params, tools):
    import json
    try:
        resultado = tools[nome]()
        retorno = resultado.run(params)
        msg = retorno.get("mensagem", retorno.get("message", json.dumps(retorno, indent=2)))
        arquivo = retorno.get("arquivo", "")
        if arquivo:
            return (
                f"**Ferramenta executada com sucesso!**\n\n"
                f"{msg}\n\n"
                f"📄 Arquivo salvo em: `{arquivo}`"
            )
        return f"**Ferramenta executada com sucesso!**\n\n{msg}"
    except Exception as e:
        return f"**Erro ao executar a ferramenta:** {str(e)}"


def _processar_automacao(pergunta, llm):
    import re
    from backend.tools import discover_tools

    global _pendente_automacao

    tools = discover_tools()

    confirmacao = ("sim", "pode", "ok", "vai", "executa", "confirmo", "pode ir", "pode executar",
                   "manda ver", "vai la", "bora", "vamos", "pode sim")
    recusa = ("nao", "não", "pare", "cancela", "nada", "depois", "agora nao", "nao quero",
              "não quero", "nem pensar", "para", "cancela isso")

    t = pergunta.lower()

    if _pendente_automacao is not None:
        if any(p in t for p in confirmacao):
            nome, params = _pendente_automacao
            _pendente_automacao = None
            print(f"[AUTOMACAO] Confirmado! Executando: {nome}")
            if nome in tools:
                return _executar_ferramenta(nome, params, tools)
            else:
                return f"A ferramenta **{nome}** não está mais disponível."
        elif any(p in t for p in recusa):
            _pendente_automacao = None
            return "Execução cancelada. Se quiser tentar outra automação, é só pedir!"
        else:
            return (
                f"Você tem uma automação pendente: **{_pendente_automacao[0]}**. "
                f"Deseja confirmar a execução? (sim/não)"
            )

    system_prompt = f"""Você está no modo **Automação** do GF Brain e NÃO é um assistente generativo.

Ferramentas disponíveis:
{_listar_ferramentas_texto(tools)}

REGRAS ABSOLUTAS:
1. NUNCA escreva poemas, textos criativos, códigos ou qualquer conteúdo que uma ferramenta deveria gerar.
2. Quando o usuário pedir para CRIAR/GERAR/FAZER algo que uma ferramenta faz, NÃO faça o trabalho da ferramenta. Em vez disso, use [EXECUTAR:nome] no final da sua resposta.
3. Se o usuário pedir informações sobre uma ferramenta, apenas explique o que ela faz — sem executar.
4. Se o usuário perguntar sobre capacidades, liste as ferramentas.
5. IMPORTANTE: SEMPRE complete as frases. Nunca pare no meio de uma frase ou raciocínio. Formate a resposta em tópicos ou bullet points sempre que possível. NÃO use asteriscos ** para negrito.

EXEMPLOS:
Usuário: "crie um poema sobre natureza"
Você: Vou criar o poema usando o gerador! [EXECUTAR:gerador_de_poema:Um poema sobre a natureza]

Usuário: "faça um poema romântico"
Você: Claro, vou executar o gerador de poemas! [EXECUTAR:gerador_de_poema:Um poema romântico]

Usuário: "do que se trata essa ferramenta de poema?"
Você: A ferramenta gerador_de_poema cria um poema personalizado e salva no Desktop.

Usuário: "oque voce sabe fazer?"
Você: Tenho a ferramenta gerador_de_poema que cria poemas personalizados.

NUNCA gere o conteúdo que a ferramenta deveria produzir. Sempre use [EXECUTAR:nome] nesses casos."""

    print(f"[AUTOMACAO] Enviando para o LLM (max_tokens=300)...")
    try:
        resposta = llm.generate(
            prompt=pergunta,
            temperature=0.3,
            max_tokens=300,
            system_prompt=system_prompt,
        )
        print(f"[AUTOMACAO] Resposta do LLM recebida ({len(resposta)} chars)")
    except Exception as e:
        print(f"[AUTOMACAO] Erro no LLM: {e}")
        return _formatar_capacidades_automacao(tools)

    match = re.search(r'\[EXECUTAR:(\w+)(?::(.+?))?\]', resposta, re.DOTALL)
    if match:
        nome = match.group(1)
        conteudo = match.group(2).strip() if match.group(2) else None
        resposta = resposta.replace(match.group(0), "").strip()
        if nome in tools:
            params = {}
            if conteudo:
                params["conteudo"] = conteudo
            _pendente_automacao = (nome, params)
            print(f"[AUTOMACAO] Marcador EXECUTAR detectado: {nome} params={params}")
            return resposta
        else:
            return (
                f"{resposta}\n\n"
                f"(A ferramenta **{nome}** não foi encontrada. "
                f"Disponíveis: {', '.join(tools.keys())})"
            )

    return resposta


def _formatar_capacidades_automacao(tools):
    nomes = list(tools.keys())
    if not nomes:
        return "Nenhuma ferramenta de automação disponível no momento."

    linhas = []
    for i, nome in enumerate(tools):
        if i >= 3:
            break
        cls = tools[nome]
        linhas.append(f"• **{nome}**: {cls.description}")

    texto = (
        "Meu escopo de **Automações** permite executar tarefas pré-definidas "
        "e determinísticas chamadas **ferramentas**.\n\n"
        f"Atualmente tenho {len(tools)} ferramenta(s) disponível(is):\n\n"
        + "\n".join(linhas)
    )

    if len(tools) > 3:
        texto += (
            f"\n\nE mais {len(tools) - 3} outra(s). "
            f"Digite **\"todas as ferramentas\"** para ver a lista completa."
        )

    texto += (
        "\n\nSe nenhuma atender o que você precisa, você mesmo pode criar novas ferramentas! "
        "É só digitar **\"como criar uma ferramenta\"** que eu explico o passo a passo.\n\n"
        "Qual delas você gostaria de executar?"
    )
    return texto


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


def responder(pergunta_original, escopo="documentacao"):
    global historico

    print(f"\n{SEPARADOR}")
    print(f"CHAT INICIADO | escopo={escopo}")
    print(f"{SEPARADOR}")
    print(f"Pergunta original: {pergunta_original}")

    intent = _detectar_saudacao(pergunta_original)
    if intent:
        print(f"[INTENT] Detectado: {intent}")
        if intent == "agradecimento":
            resposta = "Por nada! Se precisar de mais alguma coisa, é só chamar."
        else:
            resposta = SCOPE_INTRO_RESPONSES.get(escopo, SCOPE_INTRO_RESPONSES["documentacao"])
        historico.append({"pergunta": pergunta_original, "resposta": resposta})
        historico = historico[-10:]
        print(f"{SEPARADOR}\n")
        return {"resposta": resposta, "fontes": []}

    if escopo == "automacao" and _pendente_automacao is not None:
        print(f"[AUTOMACAO] Confirmacao pendente detectada")
        resposta = _processar_automacao(pergunta_original, llm)
        historico.append({"pergunta": pergunta_original, "resposta": resposta})
        historico = historico[-10:]
        print(f"{SEPARADOR}\n")
        return {"resposta": resposta, "fontes": []}

    if escopo == "automacao":
        pergunta = pergunta_original
    else:
        try:
            pergunta = reformular_pergunta(pergunta_original, historico)
        except Exception as e:
            print(f"[REFORMULAR] Erro: {e}")
            pergunta = pergunta_original

    intent_pos = _detectar_saudacao(pergunta)
    if intent_pos:
        print(f"[INTENT] Detectado (pos-reformulacao): {intent_pos}")
        if intent_pos == "agradecimento":
            resposta = "Por nada! Se precisar de mais alguma coisa, é só chamar."
        else:
            resposta = SCOPE_INTRO_RESPONSES.get(escopo, SCOPE_INTRO_RESPONSES["documentacao"])
        historico.append({"pergunta": pergunta_original, "resposta": resposta})
        historico = historico[-10:]
        print(f"{SEPARADOR}\n")
        return {"resposta": resposta, "fontes": []}

    if escopo == "automacao":
        print(f"\n[AUTOMACAO] Processando no escopo automacao...")
        resposta = _processar_automacao(pergunta_original, llm)
        historico.append({"pergunta": pergunta_original, "resposta": resposta})
        historico = historico[-10:]
        print(f"{SEPARADOR}\n")
        return {"resposta": resposta, "fontes": []}

    print(f"\n[TERMOS] Buscando termos criticos...")
    termos_criticos = extrair_termos_criticos(pergunta)
    if termos_criticos:
        print(f"[TERMOS] Encontrados: {termos_criticos}")
    else:
        print(f"[TERMOS] Nenhum termo critico encontrado")

    system_prompt = get_system_prompt(escopo)
    kb_filter = get_kb_filter(escopo)

    print(f"\n[ESCOPO] '{escopo}' -> filtro KB: {kb_filter}")

    print(f"[CHROMA] Consultando base de conhecimento...")
    results = kb_query(pergunta, n_results=10, where_filter=kb_filter)

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

    prompt = f"""Contexto extraido da base de conhecimento:
{contexto}

Com base no contexto acima, responda a pergunta abaixo.
Se o contexto nao contiver a resposta, escreva exatamente:
Nao encontrei essa informacao na documentacao disponivel.
Formate a resposta em topicos ou bullet points sempre que possivel.
 
PERGUNTA: {pergunta}
 
RESPOSTA:"""

    max_tokens_map = {"codigo": 1200, "arquitetura": 800, "documentacao": 800}
    max_tok = max_tokens_map.get(escopo, 800)

    print(f"\n[LLM] Consultando {LLM_PROVIDER} | escopo={escopo} | max_tokens={max_tok}...")
    try:
        resposta = llm.generate(
            prompt=prompt,
            temperature=0.0,
            max_tokens=max_tok,
            system_prompt=system_prompt,
        )
        print(f"[LLM] Resposta recebida ({len(resposta)} caracteres)")
    except Exception as e:
        resposta = f"Erro ao consultar a IA: {str(e)}"
        print(f"[LLM] ERRO: {e}")

    historico.append({
        "pergunta": pergunta_original,
        "resposta": resposta,
    })

    historico = historico[-10:]

    print(f"\n[FONTES] Documentos utilizados:")
    for f in fontes:
        print(f"  - {f}")
    print(f"{SEPARADOR}\n")

    return {"resposta": resposta, "fontes": list(fontes)}
