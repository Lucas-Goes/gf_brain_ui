COLLECTION_CONFIG = {
    "knowledge": {
        "metadata_schema": {
            "source": {"type": "string", "description": "Nome do arquivo de origem"},
            "chunk": {"type": "int", "description": "Índice do chunk no documento"},
            "type": {"type": "string", "description": "Tipo: doc, pattern, code"},
            "scope": {"type": "string", "description": "Escopo alvo: geral, codigo, arquitetura, documentacao, automacao"},
            "tags": {"type": "string", "description": "Tags separadas por virgula"},
        },
    },
}
