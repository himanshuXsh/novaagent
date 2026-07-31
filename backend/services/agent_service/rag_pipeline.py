import os
import uuid
import pymupdf
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# Initialize Qdrant Client (Local Disk Mode)
QDRANT_PATH = "backend/data/qdrant"
os.makedirs(QDRANT_PATH, exist_ok=True)
q_client = QdrantClient(path=QDRANT_PATH)

COLLECTION_NAME = "nova_documents"

# We'll use fastembed default model (BAAI/bge-small-en-v1.5)
q_client.set_model("BAAI/bge-small-en-v1.5")

def extract_text_from_pdf(filepath: str) -> str:
    text = ""
    with pymupdf.open(filepath) as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += (chunk_size - overlap)
    return chunks

async def process_document(filepath: str, document_id: str):
    # 1. Extract text
    full_text = extract_text_from_pdf(filepath)
    
    # 2. Chunk text
    chunks = chunk_text(full_text)
    
    # 3. Add to Qdrant (this automatically uses fastembed to generate embeddings)
    if chunks:
        # We need to construct metadata
        metadata = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        q_client.add(
            collection_name=COLLECTION_NAME,
            documents=chunks,
            metadata=metadata
        )
    
    return len(chunks)
