import json
import re
from groq import AsyncGroq
from backend.shared.config import settings

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are an expert Coding Assistant.
Your task is to provide explanations and output code.
Important: You must format the main code solution you provide inside a standard markdown code block.
Example:
```python
def example():
    pass
```
The first code block you output will be treated as the main artifact. Provide a brief explanation before or after it.
"""

async def generate_code_response(history, user_message):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
        
    messages.append({"role": "user", "content": user_message})
    
    response = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=0.2,
    )
    
    content = response.choices[0].message.content
    
    # Extract language and code from the first markdown code block
    match = re.search(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
    language = "text"
    code = ""
    
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
