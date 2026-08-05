from ddgs import DDGS
from groq import AsyncGroq

from backend.shared.config import settings

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are an expert Research Assistant that ONLY uses the provided search results to answer questions.

CRITICAL RULES — you MUST follow these without exception:
1. ONLY use information from the search results provided below. Do NOT use your training data.
2. NEVER say phrases like "As of my knowledge cutoff", "As of my last update", "Based on my training", or any similar phrase.
3. If the search results contain dates or recent information, always include them to show the answer is current.
4. You MUST cite sources using bracketed numbers like [1], [2], etc., matching the search results provided.
5. If the search results do not contain enough information to answer the question, say exactly: "The live search did not return sufficient results for this query. Please try rephrasing your question."
6. Never guess, never estimate, never fill gaps with your own knowledge.
"""

async def generate_search_response(query: str):
    snippets_text = ""
    sources = []
    images = []
    
    try:
        if settings.tavily_api_key and TavilyClient:
            tavily = TavilyClient(api_key=settings.tavily_api_key)
            response = tavily.search(query=query, search_depth="advanced", max_results=5, include_images=True)
            
            for i, res in enumerate(response.get("results", []), 1):
                sources.append({
                    "id": i,
                    "title": res.get("title", ""),
                    "url": res.get("url", ""),
                    "snippet": res.get("content", "")
                })
                snippets_text += f"Source [{i}]: {res.get('title')} ({res.get('url')})\nSnippet: {res.get('content')}\n\n"
                
            for img in response.get("images", [])[:3]:
                images.append({
                    "url": img,
                    "thumbnail_url": img
                })
        else:
            with DDGS() as ddgs:
                # Text results
                raw_results = list(ddgs.text(query, max_results=5))
                
                for i, res in enumerate(raw_results, 1):
                    sources.append({
                        "id": i,
                        "title": res.get("title", ""),
                        "url": res.get("href", ""),
                        "snippet": res.get("body", "")
                    })
                    snippets_text += f"Source [{i}]: {res.get('title')} ({res.get('href')})\nSnippet: {res.get('body')}\n\n"
                    
                # Image results
                image_results = list(ddgs.images(query, max_results=3))
                for img in image_results:
                    images.append({
                        "url": img.get("image", ""),
                        "thumbnail_url": img.get("thumbnail", img.get("image", ""))
                    })
    except Exception as e:
        snippets_text = f"Search currently unavailable. Error: {e!s}"
        sources = []
        images = []
        
    # 2. Guard: if web search returned nothing, do not call LLM — return a clean message immediately
    if not snippets_text.strip():
        import json
        yield json.dumps({"event": "metadata", "sources": [], "images": []}) + "\n"
        yield json.dumps({"event": "message", "content": "⚠️ Live web search returned no results for your query. Please try rephrasing or try again in a moment."}) + "\n"
        yield json.dumps({"event": "done", "full_answer": ""}) + "\n"
        return

    # 3. Call LLM — only reached when we have actual search results
    user_prompt = f"Query: {query}\n\nSearch Results (retrieved live from the web right now):\n{snippets_text}\n\nSynthesize an answer using ONLY the above search results with citations."
    
    import json
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            stream=True,
        )
        
        # First, yield the sources and images so the frontend can render them immediately
        yield json.dumps({
            "event": "metadata",
            "sources": sources,
            "images": images
        }) + "\n"
        
        full_answer = ""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_answer += content
                yield json.dumps({
                    "event": "message",
                    "content": content
                }) + "\n"
                
        yield json.dumps({
            "event": "done",
            "full_answer": full_answer
        }) + "\n"
    except Exception as e:
        from backend.shared.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"Search LLM generation failed: {e}")
        
        # Yield metadata anyway if we have it
        yield json.dumps({
            "event": "metadata",
            "sources": sources,
            "images": images
        }) + "\n"
        
        yield json.dumps({
            "event": "message",
            "content": "\n\n*(Error: The AI model is currently unavailable to synthesize the answer. Please check the sources above.)*"
        }) + "\n"
        
        yield json.dumps({
            "event": "done",
            "full_answer": ""
        }) + "\n"
