from groq import AsyncGroq
from backend.shared.config import settings
from backend.services.agent_service.rag_pipeline import q_client, COLLECTION_NAME
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a helpful assistant.
Use ONLY the provided context to answer the user's question.
If the context does not contain the answer, say "I cannot answer this based on the provided document."
Do not invent information.
"""

SIMILARITY_THRESHOLD = 0.5 # Strict threshold to reject off-topic questions

async def query_document(query: str, document_id: str):
    # 1. Search Qdrant
    search_result = q_client.query(
        collection_name=COLLECTION_NAME,
        query_text=query,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        ),
        limit=3
    )
    
    # search_result is a list of QueryResponse objects
    # Check if we have any good matches
    valid_chunks = []
    for res in search_result:
        if res.score >= SIMILARITY_THRESHOLD:
            valid_chunks.append(res.document)
            
    if not valid_chunks:
        return "I cannot answer this based on the provided document."
        
    # 2. Construct context
    context = "\n---\n".join(valid_chunks)
    
    prompt = f"Context:\n{context}\n\nQuestion:\n{query}"
    
    # 3. Call LLM
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    return response.choices[0].message.content
