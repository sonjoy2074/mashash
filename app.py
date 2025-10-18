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
        "highly detailed whimsical fantasy illustration, dreamy and magical atmosphere, floating grassy islands, gentle sunlight, painterly digital gouache,"
        " soft pastel color palette, Studio Ghibli-inspired composition, expressive young characters, cozy storybook aesthetic, delicate brush textures, "
        "calm and nostalgic tone, imaginative world full of warmth and wonder"
    ),
    "pastel_style": (
        "soft pastel chalk art, smooth gradients, gentle tones, cozy children’s storybook feel"
    ),
    "three_dimensional_cute_style": (
        "Ultra-detailed 3D Pixar-style cute character design, chibi proportions, big expressive eyes, "
        "soft rounded shapes, smooth glossy textures, warm natural lighting, shallow depth of field, cinematic composition, gentle pastel tones, vibrant yet realistic colors, "
        "outdoor nature background, photorealistic render with soft focus and subtle bokeh, cheerful and heartwarming mood"
    ),
    "normal_anime_style": (
    "clean anime illustration, vibrant colors, smooth cel shading, expressive eyes, "
    "sharp outlines, balanced lighting, dynamic yet simple poses, polished character design, "
    "crisp highlights and shadows, authentic Japanese anime look, "
    "studio-quality 2D style, suitable for anime series or character sheets"
    ),
    "whimsical_3d_style": (
    "whimsical 3D illustration, cinematic lighting, soft depth of field, "
    "expressive stylized characters with round faces and large eyes, detailed hair and clothing, "
    "warm color palette with natural sunlight glow, magical and emotional storytelling atmosphere, "
    "handcrafted textures with painterly realism, Pixar and DreamWorks inspired visual charm, "
    "cozy composition with playful energy and lifelike materials"
    ),
    "multimedia_book_style": (
    "storybook multimedia illustration, hand-painted textures, soft watercolor and gouache style, "
    "gentle lighting with natural shadows, warm pastel color palette, expressive and child-friendly characters, "
    "mix of 2D and 3D depth for a layered look, cozy and imaginative storytelling composition, "
    "subtle paper grain texture and painterly brush details, "
    "inspired by modern children’s picture books and digital story apps"
    ),
    "normal_cute_cartoon_style": (
    "2D cute cartoon illustration, soft pastel colors, smooth gradient shading, "
    "adorable animal characters with big expressive eyes, rounded shapes and plush details, "
    "fantasy forest scene with flowers, lanterns, and a cozy cottage, "
    "magical nighttime lighting, warm glow and gentle atmosphere, "
    "storybook-style art with charming details and balanced composition"
)


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
