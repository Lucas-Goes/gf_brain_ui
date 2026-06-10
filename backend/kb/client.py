import chromadb
from sentence_transformers import SentenceTransformer

from backend.config import CHROMA_DB_PATH

embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

_client_db = None
_collection = None


def get_collection():
    global _client_db, _collection
    if _collection is None:
        _client_db = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        _collection = _client_db.get_collection("knowledge")
    return _collection


def query_knowledge(pergunta, n_results=10, where_filter=None):
    collection = get_collection()
    pergunta_embedding = embedding_model.encode(pergunta).tolist()

    kwargs = {
        "query_embeddings": [pergunta_embedding],
        "n_results": n_results,
    }

    if where_filter:
        kwargs["where"] = where_filter
        result = collection.query(**kwargs)
        if result["documents"] and len(result["documents"][0]) > 0:
            return result
        kwargs.pop("where")

    return collection.query(**kwargs)
