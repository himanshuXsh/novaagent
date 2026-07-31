import urllib.parse
import uuid

def generate_image_url(prompt: str):
    # Pollinations.ai generates an image directly from the URL.
    # We add a random seed to ensure a unique image is generated each time, even for the same prompt.
    seed = str(uuid.uuid4())[:8]
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=1024&height=1024&nologo=true"
    return url
