import os
import subprocess
from pathlib import Path
from backend.tools.base import Tool


class GeradorDePoema(Tool):
    name = "gerador_de_poema"
    description = "Cria um poema personalizado, abre o Notepad, escreve e salva na área de trabalho"
    scope = ["automacao"]

    def run(self, params: dict) -> dict:
        desktop = Path(os.environ["USERPROFILE"]) / "Desktop"
        arquivo = desktop / "poema.txt"

        poema = params.get("conteudo", "Segredo do Universo\n\nNo silêncio do código,\num byte dança.\n\n— GF Brain")

        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(poema)

        subprocess.Popen(["notepad.exe", str(arquivo)])

        return {"status": "ok", "arquivo": str(arquivo)}
