#!/usr/bin/env python3
"""Gera um script unico que recria toda a estrutura do projeto."""

import base64, json, os, zlib
from pathlib import Path

EXCLUIR_DIRS = {".venv", "__pycache__", ".git", ".gitignore", "data", "__pycache__"}
EXCLUIR_ARQS = {".env", "bundle.py", ".gitignore"}

EXT_TEXTUAIS = {".py", ".js", ".css", ".html", ".txt", ".md", ".json", ".toml", ".cfg", ".ini", ".yml", ".yaml", ".env.example"}

def coletar_arquivos(raiz):
    arquivos = []
    for caminho in Path(raiz).rglob("*"):
        if not caminho.is_file():
            continue
        if any(p in caminho.parts for p in EXCLUIR_DIRS):
            continue
        if caminho.name in EXCLUIR_ARQS:
            continue
        arquivos.append(caminho)
    return sorted(arquivos)


def codificar(conteudo: bytes) -> str:
    return base64.b64encode(zlib.compress(conteudo)).decode()


def gerar_bundle(raiz):
    arquivos = coletar_arquivos(raiz)
    bundle = {
        "meta": {
            "nome": "gf_brain_ui",
            "total_arquivos": len(arquivos),
        },
        "arquivos": []
    }

    for caminho in arquivos:
        relativo = str(caminho.relative_to(raiz))
        dados = caminho.read_bytes()
        bundle["arquivos"].append({
            "caminho": relativo,
            "dados": codificar(dados),
        })
        print(f"  [+] {relativo} ({len(dados):,} bytes)")

    return bundle


def main():
    raiz = Path(__file__).resolve().parent
    print(f"Empacotando projeto em: {raiz}\n")

    bundle = gerar_bundle(raiz)

    script_extrair = '''#!/usr/bin/env python3
import base64, os, zlib, sys
from pathlib import Path

BUNDLE = {bundle_json}

def extrair(destino="."):
    raiz = Path(destino).resolve()
    for item in BUNDLE["arquivos"]:
        caminho = raiz / item["caminho"]
        caminho.parent.mkdir(parents=True, exist_ok=True)
        dados = zlib.decompress(base64.b64decode(item["dados"]))
        caminho.write_bytes(dados)
        print(f"  [+] {item['caminho']}")

if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "."
    extrair(destino)
    print(f"\\nProjeto extraido em: {Path(destino).resolve()}")
    print(f"Total: {BUNDLE['meta']['total_arquivos']} arquivos")
'''

    script_final = script_extrair.replace(
        "{bundle_json}",
        json.dumps(bundle, ensure_ascii=False),
        1
    )

    saida = raiz / "gf_brain_bundle.py"
    saida.write_text(script_final, encoding="utf-8")
    print(f"\nBundle gerado: {saida}")
    print(f"Total de arquivos: {bundle['meta']['total_arquivos']}")
    print(f"Tamanho do bundle: {len(script_final):,} bytes")


if __name__ == "__main__":
    main()
