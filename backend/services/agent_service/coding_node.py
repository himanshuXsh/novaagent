import re

from groq import AsyncGroq

from backend.shared.config import settings

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are an expert Coding Assistant.

LANGUAGE RULE (MANDATORY): Detect the language of the user's prompt and respond ENTIRELY in that same language.
- If the prompt is in English → respond in English only.
- If the prompt is in Hindi → respond in Hindi only.
- If the prompt is in Hinglish (mix of Hindi and English) → respond in Hinglish.
- If the prompt is in any other language → respond in that language.
- NEVER switch languages mid-response. NEVER respond in a language the user did not use.

CODE FORMATTING RULE (MANDATORY): Always wrap the main code solution in a standard markdown code block with the language identifier.
Example:
```python
def example():
    pass
```
The first code block you output will be treated as the main artifact. Provide a brief explanation before or after the code block.
"""

async def generate_code_response(history, user_message):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
        
    messages.append({"role": "user", "content": user_message})
        
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.2,
    )
    
    content = response.choices[0].message.content
    language = "text"
    code = ""
    
    match = re.search(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
    if match:
        language = match.group(1) or "text"
        code = match.group(2).strip()
        
    return {
        "text_content": content,
        "artifact": {
            "language": language,
            "code": code
        } if code else None
    }
