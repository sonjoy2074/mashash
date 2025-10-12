# app.py
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from google import genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Children’s Book Image Generator")

client = genai.Client()


STYLE_PRESETS = {
    "watercolor_style": (
        "watercolor children’s book illustration, soft edges, light pastel tones, gentle brush strokes, dreamy background"
    ),
    "color_book_style": (
        "coloring book line art, simple bold black outlines, white background, suitable for kids to color in"
    ),
    "sketch_pencil_style": (
        "pencil sketch drawing, soft graphite texture, shading lines, artistic children’s book sketch style"
    ),
    "fantasy_anime_style": (
        "fantasy anime style, vibrant colors, expressive eyes, magical background, cinematic lighting"
    ),
    "crayon_drawing_style": (
        "crayon art style, childlike texture, playful colors, hand-drawn look, kids drawing aesthetic"
    ),
    "marker_comic_style": (
        "marker comic illustration, bright saturated colors, clean outlines, energetic comic book feel"
    ),
    "pastel_style": (
        "soft pastel chalk art, smooth gradients, gentle tones, cozy children’s storybook feel"
    ),
    "three_dimensional_cut_style": (
        "3D paper cut illustration, layered paper textures, soft shadows, handcrafted diorama, storybook aesthetic"
    ),
}

@app.post("/generate")
async def generate_image(
    style: str = Form(...),
    prompt: str = Form(...),
):
    """Generate an image based on user prompt + selected illustration style"""
    if style not in STYLE_PRESETS:
        return JSONResponse(
            {"error": f"Invalid style. Choose one of: {list(STYLE_PRESETS.keys())}"},
            status_code=400,
        )

    # Combine user prompt with system style preset
    final_prompt = f"{prompt}, {STYLE_PRESETS[style]}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[final_prompt],
        )

        # Extract image
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                output_path = "generated_image.png"
                image.save(output_path)
                return FileResponse(output_path, media_type="image/png")

        return JSONResponse({"error": "No image generated."}, status_code=500)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
