import json
import httpx
from groq import AsyncGroq

from backend.shared.config import settings
from backend.shared.logger import get_logger

logger = get_logger(__name__)

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        DDGS = None

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are an expert Research Assistant.
If search results are provided, synthesize a clear, comprehensive answer using the search results and cite them using bracketed numbers like [1], [2].
If no search results are provided or live search was unavailable, provide the best possible comprehensive answer based on your knowledge, noting any temporal boundaries."""


async def _fetch_web_results(query: str):
    sources = []
    images = []

    # 1. Try Tavily first if API key is present
    if settings.tavily_api_key and TavilyClient:
        try:
            tavily = TavilyClient(api_key=settings.tavily_api_key)
            response = tavily.search(query=query, search_depth="advanced", max_results=5, include_images=True)
            for i, res in enumerate(response.get("results", []), 1):
                sources.append({
                    "id": i,
                    "title": res.get("title", ""),
                    "url": res.get("url", ""),
                    "snippet": res.get("content", "")
                })
            for img in response.get("images", [])[:3]:
                images.append({"url": img, "thumbnail_url": img})
            if sources:
                return sources, images
        except Exception as e:
            logger.warning(f"Tavily search failed ({e}), falling back to alternative.")

    # 2. Try DuckDuckGo
    if DDGS:
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=5))
                for i, res in enumerate(raw_results, 1):
                    sources.append({
                        "id": i,
                        "title": res.get("title", ""),
                        "url": res.get("href", ""),
                        "snippet": res.get("body", "")
                    })
        except Exception as e:
            logger.warning(f"DDGS text search error: {e}")

        # Image search in separate try-except so an image failure never cancels text results
        try:
            with DDGS() as ddgs:
                image_results = list(ddgs.images(query, max_results=3))
                for img in image_results:
                    images.append({
                        "url": img.get("image", ""),
                        "thumbnail_url": img.get("thumbnail", img.get("image", ""))
                    })
        except Exception as e:
            logger.warning(f"DDGS image search skipped/failed: {e}")

    # 3. Wikipedia API fallback if 0 sources found
    if not sources:
        try:
            async with httpx.AsyncClient(timeout=6.0) as http_client:
                wiki_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=3&namespace=0&format=json"
                resp = await http_client.get(wiki_url)
                if resp.status_code == 200:
                    data = resp.json()
                    titles = data[1] if len(data) > 1 else []
                    snippets = data[2] if len(data) > 2 else []
                    urls = data[3] if len(data) > 3 else []
                    for i, (title, snippet, url) in enumerate(zip(titles, snippets, urls), 1):
                        if snippet:
                            sources.append({
                                "id": i,
                                "title": title,
                                "url": url,
                                "snippet": snippet
                            })
        except Exception as e:
            logger.warning(f"Wikipedia fallback search failed: {e}")

    return sources, images


async def generate_search_response(query: str):
    sources, images = await _fetch_web_results(query)

    snippets_text = ""
    for s in sources:
        snippets_text += f"Source [{s['id']}]: {s['title']} ({s['url']})\nSnippet: {s['snippet']}\n\n"

    # First, yield the metadata (sources and images) immediately to the frontend
    yield json.dumps({
        "event": "metadata",
        "sources": sources,
        "images": images
    }) + "\n"

    prefix_notice = ""
    if sources:
        user_prompt = f"Query: {query}\n\nSearch Results (retrieved live from the web):\n{snippets_text}\n\nSynthesize a clear, detailed answer using the above search results with citations [1], [2]."
    else:
        prefix_notice = "*(Note: Live search returned 0 external sources. Answering using NovaAgent AI knowledge base:)*\n\n"
        user_prompt = f"Query: {query}\n\nPlease provide a clear, comprehensive, and helpful answer to this query based on your knowledge."

    try:
        response = await client.chat.completions.create(
            model=settings.groq_fast_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            stream=True,
        )

        full_answer = ""
        if prefix_notice:
            full_answer += prefix_notice
            yield json.dumps({
                "event": "message",
                "content": prefix_notice
            }) + "\n"

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
        logger.error(f"Search LLM generation failed: {e}")
        yield json.dumps({
            "event": "message",
            "content": f"\n\n*(Error: The AI model encountered an issue: {e!s})*"
        }) + "\n"
        yield json.dumps({
            "event": "done",
            "full_answer": ""
        }) + "\n"
