from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from google import genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Children’s Book Image Generator with Styles & Shapes")

client = genai.Client()


# STYLE PRESETS

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
    ),
}

# =====================
# BOOK PRESETS
# =====================
BOOK_PRESETS = {
    "magic_book": {
        "name": "Magic Book",
        "size": "square",
        "aspect_ratio": "1:1",
        "description": "square format children's book illustration, magical storybook composition, centered layout"
    },
    "story_book": {
        "name": "Story Book",
        "size": "6x9",
        "aspect_ratio": "2:3",
        "description": "6x9 portrait format illustration, classic storybook layout, vertical composition"
    },
    "pocket_book": {
        "name": "Pocket Book",
        "size": "5x7",
        "aspect_ratio": "5:7",
        "description": "5x7 compact portrait format, pocket-sized book illustration, cozy composition"
    },
    "dream_book": {
        "name": "Dream Book",
        "size": "8x10",
        "aspect_ratio": "4:5",
        "description": "8x10 large portrait format, dreamy storybook illustration, expansive composition"
    },
    "art_book": {
        "name": "Art Book",
        "size": "6x8",
        "aspect_ratio": "3:4",
        "description": "6x8 portrait format, artistic book illustration, gallery-style composition"
    },
    "mini_book": {
        "name": "Mini Book",
        "size": "6x4",
        "aspect_ratio": "3:2",
        "description": "6x4 landscape format, mini book illustration, wide horizontal composition"
    },
}


# =====================
# Main Endpoint
# =====================
@app.post("/generate")
async def generate_image(
    style: str = Form(...),
    book: str = Form("dream_book"),
    prompt: str = Form(...),
):
    """Generate an image using selected style + book format context."""
    if style not in STYLE_PRESETS:
        return JSONResponse(
            {"error": f"Invalid style. Choose one of: {list(STYLE_PRESETS.keys())}"},
            status_code=400,
        )

    if book not in BOOK_PRESETS:
        return JSONResponse(
            {"error": f"Invalid book format. Choose one of: {list(BOOK_PRESETS.keys())}"},
            status_code=400,
        )

    # Combine user input + style + book format context for Gemini
    book_info = BOOK_PRESETS[book]
    final_prompt = (
        f"{prompt}, {STYLE_PRESETS[style]}, "
        f"{book_info['description']}, storybook composition, children-friendly art"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[final_prompt],
        )

        # Extract generated image
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                output_path = f"generated_{book}_{style}.png"
                image.save(output_path)
                return FileResponse(output_path, media_type="image/png")

        return JSONResponse({"error": "No image generated."}, status_code=500)
      
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
