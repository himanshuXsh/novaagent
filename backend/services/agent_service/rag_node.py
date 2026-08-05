from groq import AsyncGroq
from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from backend.services.agent_service.rag_pipeline import (
    COLLECTION_NAME,
    VECTOR_SIZE,
    _embed_model,
    q_client,
)
from backend.shared.config import settings
from backend.shared.logger import get_logger

logger = get_logger(__name__)

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a helpful document assistant.
Use the provided context to answer the user's question as accurately as possible.
If the context contains relevant information, use it to give a complete, helpful answer.
If the context truly does not contain any relevant information to answer the question, say so briefly.
Do not invent facts not supported by the context.
"""


async def query_document(query: str, document_id: str):
    # 1. Guard checks
    if q_client is None:
        logger.error("q_client is None — Qdrant not initialized")
        return "System Error: The document vector database is currently offline. Please try again later."

    if _embed_model is None:
        logger.error("Embedding model is None — fastembed not initialized")
        return "System Error: The embedding model failed to load. Please restart the service."

    # 2. Embed the query using the same model used during upload
    try:
        query_embedding = list(_embed_model.embed([query]))[0].tolist()
    except Exception as e:
        logger.error(f"Failed to embed query: {e}", exc_info=True)
        return "System Error: Failed to process your query. Please try again."

    # 3. Search Qdrant using stable low-level search() API
    search_result = []
    try:
        result = q_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            ),
            limit=10,
            with_payload=True,
        )
        search_result = result.points
        logger.info(f"Qdrant query_points returned {len(search_result)} results for doc {document_id}")
    except Exception as e:
        logger.error(f"Qdrant query_points() failed ({type(e).__name__}: {e})", exc_info=True)
        return "System Error: Failed to retrieve document context from the database."


    # 4. Extract text from point payloads
    valid_chunks = []
    for point in search_result:
        if point.payload:
            text = point.payload.get("document") or point.payload.get("text") or ""
            if text:
                valid_chunks.append(text)

    logger.info(f"RAG extracted {len(valid_chunks)} valid chunks")

    if not valid_chunks:
        return "I could not find relevant information in your document to answer this question."

    # 5. Construct context and call LLM
    context = "\n---\n".join(valid_chunks)
    prompt = f"Context:\n{context}\n\nQuestion:\n{query}"

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"RAG LLM generation failed: {e}", exc_info=True)
        return "System Error: The AI model timed out or is currently unavailable. Please try your request again."
