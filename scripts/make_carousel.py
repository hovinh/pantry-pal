"""
Generate a LinkedIn carousel (7 slides, 1080x1080 PNG each) for Pantry Pal.

Usage:
    python scripts/make_carousel.py [--screenshots scripts/carousel_screenshots]
                                    [--out scripts/carousel_output]

Outputs:
    slide_01_cover.png  through  slide_07_cta.png
    carousel.pdf        (all slides combined, ready to upload to LinkedIn)
"""

import argparse
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG          = "#FFFFFF"
C_DARK_GREEN  = "#1B4332"
C_MED_GREEN   = "#2D6A4F"
C_LIGHT_GREEN = "#52B788"
C_PALE_GREEN  = "#D8F3DC"
C_TEXT        = "#1A1A2E"
C_SUBTEXT     = "#4A5568"
C_WHITE       = "#FFFFFF"
C_ACCENT      = "#40916C"

W, H = 1080, 1080

FONT_BOLD   = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG    = "C:/Windows/Fonts/arial.ttf"
FONT_ITALIC = "C:/Windows/Fonts/ariali.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, size)


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def new_canvas(bg: str = C_BG) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), hex_to_rgb(bg))
    return img, ImageDraw.Draw(img)


def draw_text_wrapped(draw, text, x, y, max_width, fnt, fill, line_spacing=8):
    """Draw text wrapped at max_width pixels, return final y position."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    cy = y
    for line in lines:
        draw.text((x, cy), line, font=fnt, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=fnt)
        cy += (bbox[3] - bbox[1]) + line_spacing
    return cy


def draw_slide_number(draw, n, total=7):
    fnt = font(22)
    text = f"{n} / {total}"
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = W - bbox[2] - 32
    y = H - bbox[3] - 24
    draw.text((x, y), text, font=fnt, fill=hex_to_rgb(C_SUBTEXT))


def draw_swipe_hint(draw):
    fnt = font(22)
    text = "Swipe →"
    draw.text((W // 2 - 36, H - 52), text, font=fnt, fill=hex_to_rgb(C_LIGHT_GREEN))


def draw_brand_tag(draw):
    fnt = font(22)
    draw.text((32, H - 52), "Pantry Pal", font=fnt, fill=hex_to_rgb(C_LIGHT_GREEN))


def paste_screenshot(img, ss_path, x, y, w, h, radius=16):
    """Paste a screenshot resized to (w, h) at (x, y) with rounded corners."""
    if not os.path.exists(ss_path):
        return
    ss = Image.open(ss_path).convert("RGBA")
    ss = ss.resize((w, h), Image.LANCZOS)

    # Rounded-corner mask
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    ss.putalpha(mask)

    img.paste(ss, (x, y), ss)


# ── Slide builders ────────────────────────────────────────────────────────────

def slide_01_cover(ss_dir: str) -> Image.Image:
    """Dark green cover with app name, tagline, and a strip of recipe images."""
    img, draw = new_canvas(C_DARK_GREEN)

    # Top accent bar
    draw.rectangle([0, 0, W, 6], fill=hex_to_rgb(C_LIGHT_GREEN))

    # App name
    draw.text((60, 90), "Pantry Pal", font=font(64, bold=True), fill=hex_to_rgb(C_WHITE))

    # Tagline
    draw.text((60, 170), "A side project born out of love", font=font(32), fill=hex_to_rgb(C_PALE_GREEN))

    # Main headline
    draw_text_wrapped(
        draw,
        "I built an app so my wife never has to ask 'what's for dinner?' again.",
        60, 260, W - 120, font(48, bold=True), hex_to_rgb(C_WHITE), line_spacing=12,
    )

    # Feature teasers
    features = [
        "01  Quick recipe reminder",
        "02  Nutrition at a glance",
        "03  Smart shopping checklist",
    ]
    fy = 500
    for label in features:
        draw.text((60, fy), label, font=font(30), fill=hex_to_rgb(C_PALE_GREEN))
        fy += 52

    # Recipe gallery screenshot strip at bottom
    ss_path = os.path.join(ss_dir, "1_recipe_gallery.png")
    if os.path.exists(ss_path):
        ss = Image.open(ss_path).convert("RGBA")
        # Crop to the card grid area (right portion, skip sidebar)
        crop = ss.crop((290, 60, ss.width, ss.height))
        target_w = W - 60
        target_h = int(crop.height * target_w / crop.width)
        crop = crop.resize((target_w, min(target_h, 300)), Image.LANCZOS)
        # Fade bottom edge
        fade = Image.new("RGBA", crop.size, (0, 0, 0, 0))
        fd = ImageDraw.Draw(fade)
        for i in range(80):
            alpha = int(255 * (i / 80))
            y_line = crop.height - 80 + i
            if 0 <= y_line < crop.height:
                fd.line([(0, y_line), (crop.width, y_line)], fill=(27, 67, 50, alpha))
        crop = Image.alpha_composite(crop, fade)
        img.paste(crop, (30, H - crop.height - 60), crop)

    draw_slide_number(draw, 1)
    draw_swipe_hint(draw)
    return img


def slide_02_problem(ss_dir: str) -> Image.Image:
    """The relatable problem story."""
    img, draw = new_canvas(C_BG)

    # Left accent bar
    draw.rectangle([0, 0, 8, H], fill=hex_to_rgb(C_MED_GREEN))
    draw_brand_tag(draw)

    draw.text((52, 80), "The story", font=font(28), fill=hex_to_rgb(C_ACCENT))
    draw.text((52, 120), "Sound familiar?", font=font(56, bold=True), fill=hex_to_rgb(C_TEXT))
    draw.line([(52, 200), (W - 52, 200)], fill=hex_to_rgb(C_PALE_GREEN), width=2)

    problems = [
        ("01", "Has 30 recipes in her head but forgets half at the wrong moment"),
        ("02", "No idea which meal is actually good for the family"),
        ("03", "Supermarket trips without a plan means forgetting things and impulse buying"),
    ]

    py = 240
    for num, text in problems:
        # Numbered bubble
        draw.ellipse([52, py, 52 + 64, py + 64], fill=hex_to_rgb(C_PALE_GREEN))
        draw.text((52 + 14, py + 14), num, font=font(26, bold=True), fill=hex_to_rgb(C_MED_GREEN))
        draw_text_wrapped(draw, text, 140, py + 12, W - 180, font(28), hex_to_rgb(C_TEXT), line_spacing=6)
        py += 120

    draw.text((52, py + 16), "So I built her something.", font=font(36, bold=True), fill=hex_to_rgb(C_MED_GREEN))
    draw_slide_number(draw, 2)
    draw_swipe_hint(draw)
    return img


def _feature_slide(n, icon, title, subtitle, desc_lines, ss_path, slide_num) -> Image.Image:
    img, draw = new_canvas(C_BG)
    draw.rectangle([0, 0, W, 8], fill=hex_to_rgb(C_MED_GREEN))
    draw_brand_tag(draw)

    # Header
    draw.text((52, 40), f"Feature {n}", font=font(26), fill=hex_to_rgb(C_ACCENT))
    draw.text((52, 78), title, font=font(52, bold=True), fill=hex_to_rgb(C_TEXT))
    draw.text((52, 142), subtitle, font=font(28), fill=hex_to_rgb(C_SUBTEXT))
    draw.line([(52, 188), (W - 52, 188)], fill=hex_to_rgb(C_PALE_GREEN), width=2)

    # Screenshot
    ss_y = 208
    ss_h = 520
    ss_w = W - 104
    if os.path.exists(ss_path):
        # Drop shadow
        shadow = Image.new("RGBA", (ss_w + 8, ss_h + 8), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle([4, 4, ss_w + 8, ss_h + 8], radius=16, fill=(0, 0, 0, 60))
        img.paste(shadow, (52 - 4, ss_y - 4), shadow)
        paste_screenshot(img, ss_path, 52, ss_y, ss_w, ss_h)

    # Description bullets
    dy = ss_y + ss_h + 24
    for line in desc_lines:
        draw.text((52, dy), f"• {line}", font=font(26), fill=hex_to_rgb(C_TEXT))
        dy += 40

    draw_slide_number(draw, slide_num)
    draw_swipe_hint(draw)
    return img


def slide_03_gallery(ss_dir: str) -> Image.Image:
    ss = os.path.join(ss_dir, "1_recipe_gallery.png")
    # Crop sidebar out
    if os.path.exists(ss):
        orig = Image.open(ss)
        cropped = orig.crop((290, 0, orig.width, orig.height))
        tmp = os.path.join(ss_dir, "_gallery_crop.png")
        cropped.save(tmp)
        ss = tmp

    return _feature_slide(
        1, "📋", "Recipe Gallery", "Browse all your dishes at a glance",
        ["Watercolour dish illustrations", "Search by name or cuisine", "Full instructions on each card"],
        ss, 3,
    )


def slide_04_nutrition(ss_dir: str) -> Image.Image:
    return _feature_slide(
        2, "📊", "Nutrition Info", "Know exactly what you're eating",
        ["Per-serving calorie & macro breakdown", "Bar chart vs daily recommended intake", "Radar chart for nutritional balance"],
        os.path.join(ss_dir, "2_nutrition.png"), 4,
    )


def slide_05_picker(ss_dir: str) -> Image.Image:
    return _feature_slide(
        3, "🛒", "Ingredient Picker", "Plan your supermarket trip in seconds",
        ["Tick what's already in your pantry", "App ranks recipes by match %", "Green = you have it  ·  Yellow = buy it"],
        os.path.join(ss_dir, "3_ingredient_picker.png"), 5,
    )


def slide_06_tech(ss_dir: str) -> Image.Image:
    img, draw = new_canvas(C_DARK_GREEN)
    draw.rectangle([0, 0, W, 8], fill=hex_to_rgb(C_LIGHT_GREEN))
    draw_brand_tag(draw)

    draw.text((52, 60), "Built with", font=font(34), fill=hex_to_rgb(C_PALE_GREEN))
    draw.text((52, 106), "Simple tools,\nbig impact.", font=font(62, bold=True), fill=hex_to_rgb(C_WHITE))
    draw.line([(52, 250), (W - 52, 250)], fill=hex_to_rgb(C_MED_GREEN), width=2)

    stack = [
        ("Py", "Python 3.11",       "Core language"),
        ("ST", "Streamlit",         "Web UI in pure Python — no JS needed"),
        ("YM", "YAML",              "Recipes & ingredients as plain text files"),
        ("PL", "Pillow / Plotly",   "Image handling & nutrition charts"),
    ]
    sy = 280
    for abbr, name, desc in stack:
        draw.ellipse([52, sy, 52 + 56, sy + 56], fill=hex_to_rgb(C_MED_GREEN))
        draw.text((52 + 8, sy + 12), abbr, font=font(22, bold=True), fill=hex_to_rgb(C_WHITE))
        draw.text((128, sy + 4), name, font=font(30, bold=True), fill=hex_to_rgb(C_WHITE))
        draw.text((128, sy + 38), desc, font=font(22), fill=hex_to_rgb(C_PALE_GREEN))
        sy += 96

    draw.text((52, sy + 20), "100% open source on GitHub", font=font(28), fill=hex_to_rgb(C_LIGHT_GREEN))

    draw_slide_number(draw, 6)
    draw_swipe_hint(draw)
    return img


def slide_07_cta(ss_dir: str) -> Image.Image:
    img, draw = new_canvas(C_BG)
    draw.rectangle([0, 0, W, 8], fill=hex_to_rgb(C_MED_GREEN))
    draw_brand_tag(draw)

    # Central message
    draw.text((52, 80), "Would your partner\nfind this useful?", font=font(60, bold=True), fill=hex_to_rgb(C_TEXT))

    draw.line([(52, 280), (W - 52, 280)], fill=hex_to_rgb(C_PALE_GREEN), width=2)

    bullets = [
        "->  GitHub link in the comments",
        "->  Star the repo if it sparks an idea",
        "->  Comment what feature you'd add next",
        "->  Repost to reach other builders",
    ]
    by = 310
    for b in bullets:
        draw_text_wrapped(draw, b, 52, by, W - 104, font(30), hex_to_rgb(C_TEXT), line_spacing=4)
        by += 72

    # Bottom pill
    pill_y = H - 160
    draw.rounded_rectangle([52, pill_y, W - 52, pill_y + 80], radius=40, fill=hex_to_rgb(C_MED_GREEN))
    draw.text((W // 2 - 220, pill_y + 18), "Built with Python + Streamlit", font=font(30, bold=True), fill=hex_to_rgb(C_WHITE))

    draw_slide_number(draw, 7)
    return img


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshots", default="scripts/carousel_screenshots")
    parser.add_argument("--out", default="scripts/carousel_output")
    args = parser.parse_args()

    ss = args.screenshots
    out = args.out
    os.makedirs(out, exist_ok=True)

    builders = [
        ("slide_01_cover",    slide_01_cover),
        ("slide_02_problem",  slide_02_problem),
        ("slide_03_gallery",  slide_03_gallery),
        ("slide_04_nutrition",slide_04_nutrition),
        ("slide_05_picker",   slide_05_picker),
        ("slide_06_tech",     slide_06_tech),
        ("slide_07_cta",      slide_07_cta),
    ]

    slides = []
    for name, fn in builders:
        img = fn(ss)
        path = os.path.join(out, f"{name}.png")
        img.save(path)
        print(f"Saved: {path}")
        slides.append(img.convert("RGB"))

    # Export combined PDF using img2pdf
    import img2pdf
    png_paths = [os.path.join(out, f"{name}.png") for name, _ in builders]
    pdf_path = os.path.join(out, "carousel.pdf")
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(png_paths))
    print(f"\nPDF saved: {pdf_path}")
    print(f"\nDone — {len(slides)} slides in {out}/")


if __name__ == "__main__":
    main()
