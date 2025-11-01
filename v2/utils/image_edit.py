from PIL import Image, ImageOps, ImageStat
from collections import Counter
import colorsys
import hashlib
import io
import base64

def get_accent_color(img, n_colors=5, min_saturation=0.2):
    """
    Returns an accent color (a dominant, non-grayish color) from an image.
    """

    # Convert to RGB and reduce size for speed
    img = img.convert("RGB").resize((64, 64))

    # Get pixel data
    pixels = list(img.getdata())

    # Convert to HSV to filter by saturation
    hsv_pixels = [colorsys.rgb_to_hsv(r/255, g/255, b/255) for r, g, b in pixels]

    # Filter out low-saturation pixels (grays)
    colorful_pixels = [
        (int(r), int(g), int(b))
        for (r, g, b), (h, s, v) in zip(pixels, hsv_pixels)
        if s > min_saturation and v > 0.15
    ]

    if not colorful_pixels:
        # fallback: just take mean color if image is truly grayscale
        return tuple(int(sum(c)/len(c)) for c in zip(*pixels))

    # Count most common colors
    color_counts = Counter(colorful_pixels)
    accent_color = color_counts.most_common(1)[0][0]

    return accent_color


def resize_with_fill(img, size=(128, 128), fill="auto"):
    """
    Resize an image to `size`, keeping aspect ratio and filling the remaining
    space with a solid color (dominant or specified).
    """

    # If fill='auto', compute an approximate dominant color
    if fill == "auto":
        fill = get_accent_color(img)

    # Make sure we're working in RGB
    img = img.convert("RGB")

    # Fit inside target while keeping ratio
    img.thumbnail(size, Image.Resampling.LANCZOS)

    # Create background
    background = Image.new("RGB", size, fill)

    # Center paste
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    background.paste(img, offset)

    return background


def file_hash(f):
    """Compute a simple hash for the uploaded file content."""
    f.seek(0)
    h = hashlib.sha256(f.read()).hexdigest()
    f.seek(0)  # Reset pointer so PIL can read it
    return h


def pil_to_base64(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")  # or JPEG
    buffer.seek(0)
    img_bytes = buffer.read()
    return base64.b64encode(img_bytes).decode()