import os
import chromadb

from sentence_transformers import SentenceTransformer
from backend.config import CHROMA_DB_PATH, DOCS_PATH

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(
    path=CHROMA_DB_PATH
)

collection = client.get_or_create_collection(
    name="knowledge"
)


def chunk_text(text, chunk_size=800, overlap=100):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(
            text[start:end]
        )

        start += chunk_size - overlap

    return chunks


total_chunks = 0

for file in os.listdir(DOCS_PATH):

    if not file.endswith(".txt"):
        continue

    filepath = os.path.join(
        DOCS_PATH,
        file
    )

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        text = f.read()

    chunks = chunk_text(
        text,
        CHUNK_SIZE,
        CHUNK_OVERLAP
    )

    for idx, chunk in enumerate(chunks):

        embedding = model.encode(
            chunk
        ).tolist()

        collection.add(
            ids=[
                f"{file}_chunk_{idx}"
            ],
            documents=[
                chunk
            ],
            embeddings=[
                embedding
            ],
            metadatas=[
                {
                    "source": file,
                    "chunk": idx
                }
            ]
        )

        total_chunks += 1

    print(
        f"{file}: {len(chunks)} chunks"
    )

print("\n===================")
print(f"Total de chunks: {total_chunks}")
print("===================")
