import gc
import os
import uuid

import pymupdf
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from backend.shared.logger import get_logger

logger = get_logger(__name__)

# Initialize Qdrant Client (Local Disk Mode)
QDRANT_PATH = os.environ.get("QDRANT_PATH", "/app/backend/data/qdrant")
os.makedirs(QDRANT_PATH, exist_ok=True)

try:
    q_client = QdrantClient(path=QDRANT_PATH)
except Exception as e:
    logger.error(f"Failed to initialize QdrantClient: {e}")
    q_client = None

COLLECTION_NAME = "nova_documents"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE = 384  # bge-small-en-v1.5 produces 384-dim vectors

# Load embedding model once at module level (cached after first load)
try:
    _embed_model = TextEmbedding(EMBED_MODEL)
    logger.info(f"Embedding model '{EMBED_MODEL}' loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    _embed_model = None


def _ensure_collection():
    """Create or verify the Qdrant collection. Recreates if schema is incompatible."""
    try:
        exists = q_client.collection_exists(COLLECTION_NAME)
        if exists:
            try:
                info = q_client.get_collection(COLLECTION_NAME)
                vectors_config = info.config.params.vectors

                # Determine if collection uses named vectors (old fastembed API)
                # vs unnamed default vector (our new API)
                needs_recreate = False

                if isinstance(vectors_config, dict):
                    # Named-vector collection — old fastembed format. Must recreate.
                    logger.warning(
                        f"Collection '{COLLECTION_NAME}' uses named vectors "
                        f"({list(vectors_config.keys())}). Recreating with unnamed default vector."
                    )
                    needs_recreate = True
                elif hasattr(vectors_config, 'size'):
                    # Unnamed vector — check dimension
                    if vectors_config.size != VECTOR_SIZE:
                        logger.warning(
                            f"Collection '{COLLECTION_NAME}' vector size mismatch "
                            f"({vectors_config.size} vs {VECTOR_SIZE}). Recreating."
                        )
                        needs_recreate = True
                    else:
                        logger.info(f"Collection '{COLLECTION_NAME}' OK (unnamed, dim={vectors_config.size})")

                if needs_recreate:
                    q_client.delete_collection(COLLECTION_NAME)
                    exists = False

            except Exception as check_err:
                logger.warning(f"Could not verify collection schema ({check_err}). Proceeding anyway.")

        if not exists:
            q_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection '{COLLECTION_NAME}' (unnamed default, dim={VECTOR_SIZE})")
        return True
    except Exception as e:
        logger.error(f"Failed to ensure Qdrant collection: {e}", exc_info=True)
        return False




MAX_PAGES = 50
MAX_CHUNKS = 150

def extract_text_from_pdf(filepath: str, max_pages: int = MAX_PAGES) -> str:
    text = ""
    with pymupdf.open(filepath) as doc:
        for i, page in enumerate(doc):
            if i >= max_pages:
                logger.info(f"Reached max page limit of {max_pages} pages.")
                break
            text += page.get_text() + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50, max_chunks: int = MAX_CHUNKS) -> list[str]:
    chunks = []
    start = 0
    while start < len(text) and len(chunks) < max_chunks:
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += (chunk_size - overlap)
    return chunks


async def process_document(filepath: str, document_id: str):
    if q_client is None:
        raise RuntimeError("Qdrant client is not available.")
    if _embed_model is None:
        raise RuntimeError("Embedding model is not available.")

    # 1. Extract text with page limit to protect memory
    full_text = extract_text_from_pdf(filepath)
    logger.info(f"Extracted {len(full_text)} chars from document {document_id}")

    # 2. Chunk text with chunk limit
    chunks = chunk_text(full_text)
    logger.info(f"Created {len(chunks)} chunks for document {document_id}")

    if not chunks:
        return 0

    # 3. Ensure collection exists
    if not _ensure_collection():
        raise RuntimeError("Could not create or access Qdrant collection.")

    # 4. Generate embeddings and upsert in small batches of 16 to keep RAM strictly below 512MB
    batch_size = 16
    total_upserted = 0
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_embeddings = list(_embed_model.embed(batch_chunks))
        
        points = []
        for j, (chunk, embedding) in enumerate(zip(batch_chunks, batch_embeddings)):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "document_id": document_id,
                    "chunk_index": i + j,
                    "document": chunk,
                }
            ))

        try:
            q_client.upsert(collection_name=COLLECTION_NAME, points=points)
            total_upserted += len(points)
        except Exception as e:
            logger.error(f"Qdrant upsert failed ({type(e).__name__}: {e})", exc_info=True)
            raise RuntimeError(f"Qdrant upsert failed: {e}") from e

    gc.collect()
    logger.info(f"Upserted {total_upserted} vectors into Qdrant for document {document_id}")
    return total_upserted

