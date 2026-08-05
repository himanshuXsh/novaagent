import urllib.parse
import uuid


def generate_image_url(prompt: str):
    import re
    # Pollinations.ai generates an image directly from the URL.
    # We add a random seed to ensure a unique image is generated each time.
    seed = str(uuid.uuid4())[:8]
    safe_prompt = prompt.strip().replace("\n", " ").replace("\r", "")
    
    # Pollinations API throws 500 errors if the prompt starts with "generate" or "create"
    safe_prompt = re.sub(r"^(generate|create)\s+", "", safe_prompt, flags=re.IGNORECASE)
    
    encoded_prompt = urllib.parse.quote(safe_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&nologo=true"
    return url
