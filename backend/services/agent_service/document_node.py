import os
import json
import uuid
from reportlab.pdfgen import canvas
from pptx import Presentation
from groq import AsyncGroq
from backend.shared.config import settings

client = AsyncGroq(api_key=settings.groq_api_key)
OUTPUT_DIR = "backend/data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PDF_PROMPT = """You are an expert Document Generator.
Create a structured report based on the user's prompt. 
Output ONLY valid JSON in this format:
{
    "title": "Document Title",
    "paragraphs": ["paragraph 1", "paragraph 2", "etc"]
}
"""

PPT_PROMPT = """You are an expert Presentation Generator.
Create a structured presentation based on the user's prompt.
Output ONLY valid JSON in this format:
{
    "title": "Presentation Title",
    "slides": [
        {
            "title": "Slide 1 Title",
            "content": ["Bullet 1", "Bullet 2"]
        }
    ]
}
"""

async def generate_pdf_document(prompt: str):
    response = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": PDF_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    c = canvas.Canvas(filepath)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, data.get("title", "Report"))
    
    c.setFont("Helvetica", 12)
    y = 700
    for p in data.get("paragraphs", []):
        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
        c.drawString(72, y, p[:100] + ("..." if len(p) > 100 else "")) # simplified wrapping
        y -= 20
        
    c.save()
    
    return {
        "title": data.get("title", "Report"),
        "filepath": filepath,
        "filename": filename,
        "format": "pdf"
    }

async def generate_ppt_document(prompt: str):
    response = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": PPT_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pptx"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    prs = Presentation()
    
    # Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    title.text = data.get("title", "Presentation")
    
    # Content Slides
    bullet_slide_layout = prs.slide_layouts[1]
    for s_data in data.get("slides", []):
        slide = prs.slides.add_slide(bullet_slide_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        body_shape = shapes.placeholders[1]
        
        title_shape.text = s_data.get("title", "Slide")
        tf = body_shape.text_frame
        
        for i, bullet in enumerate(s_data.get("content", [])):
            if i == 0:
                tf.text = bullet
            else:
                p = tf.add_paragraph()
                p.text = bullet
                p.level = 0
                
    prs.save(filepath)
    
    return {
        "title": data.get("title", "Presentation"),
        "filepath": filepath,
        "filename": filename,
        "format": "pptx"
    }
