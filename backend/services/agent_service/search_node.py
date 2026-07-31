import json
from duckduckgo_search import DDGS
from groq import AsyncGroq
from backend.shared.config import settings

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are an expert Research Assistant.
Given the user's query and the search results provided, synthesize a clear, comprehensive answer.
You MUST cite your sources using bracketed numbers like [1], [2], etc., corresponding to the search results provided.
"""

async def generate_search_response(query: str):
    # 1. Search the web
    ddgs = DDGS()
    
    # Text results
    raw_results = list(ddgs.text(query, max_results=5))
    
    # Image results
    image_results = list(ddgs.images(query, max_results=3))
    
    sources = []
    snippets_text = ""
    
    for i, res in enumerate(raw_results, 1):
        sources.append({
            "id": i,
            "title": res.get("title", ""),
            "url": res.get("href", ""),
            "snippet": res.get("body", "")
        })
        snippets_text += f"Source [{i}]: {res.get('title')} ({res.get('href')})\nSnippet: {res.get('body')}\n\n"
        
    images = []
    for img in image_results:
        images.append({
            "url": img.get("image", ""),
            "thumbnail_url": img.get("thumbnail", img.get("image", ""))
        })
        
    # 2. Call LLM
    user_prompt = f"Query: {query}\n\nSearch Results:\n{snippets_text}\n\nPlease synthesize an answer with citations."
    
    response = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
    )
    
    answer = response.choices[0].message.content
    
    return {
        "answer": answer,
        "sources": sources,
        "images": images
    }
