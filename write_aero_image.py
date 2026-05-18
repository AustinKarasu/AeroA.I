from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / 'images'
IMAGE_DIR.mkdir(exist_ok=True)


def font(size, bold=False):
    names = (
        'arialbd.ttf',
        'segoeuib.ttf',
    ) if bold else (
        'arial.ttf',
        'segoeui.ttf',
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_logo(path):
    width, height = 900, 680
    image = Image.new('RGB', (width, height), '#f7f9fb')
    draw = ImageDraw.Draw(image)

    navy = '#07365b'
    teal = '#00a6d6'
    gold = '#f6b735'
    bronze = '#80673f'

    # Aero mark: upward motion wing and arrow.
    draw.polygon([(260, 390), (570, 150), (510, 360), (430, 305)], fill=navy)
    draw.polygon([(310, 390), (570, 150), (530, 340), (450, 305)], fill=gold)
    draw.polygon([(220, 430), (510, 350), (475, 385), (295, 455)], fill=teal)
    draw.polygon([(250, 475), (485, 395), (455, 425), (320, 500)], fill=navy)
    draw.arc((150, 330, 570, 560), start=8, end=70, fill=teal, width=16)
    draw.arc((180, 350, 545, 570), start=8, end=66, fill='#ffffff', width=5)
    draw.arc((210, 375, 525, 585), start=8, end=64, fill='#3cc7e8', width=7)
    draw.polygon([(560, 145), (605, 95), (585, 265)], fill=gold)
    draw.polygon([(585, 265), (560, 145), (545, 325)], fill='#d0922e')
    draw.line((588, 166, 610, 138), fill='#fff1a8', width=5)
    draw.line((615, 260, 635, 260), fill=gold, width=4)
    draw.line((625, 250, 625, 270), fill=gold, width=4)

    title_font = font(84, bold=True)
    subtitle_font = font(28)
    title = 'AERO'
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((title_x, 510), title, font=title_font, fill=navy)
    draw.text((title_x + 252, 510), ' A.I', font=title_font, fill=bronze)

    subtitle = 'Local intelligent assistant'
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    draw.text(((width - (bbox[2] - bbox[0])) // 2, 610), subtitle, font=subtitle_font, fill='#4f6372')

    image.save(path, quality=95)


def draw_assistant(path):
    width, height = 1200, 720
    image = Image.new('RGB', (width, height), '#0b1015')
    draw = ImageDraw.Draw(image)

    for y in range(height):
        shade = int(15 + (y / height) * 24)
        draw.line((0, y, width, y), fill=(shade // 2, shade, shade + 8))

    cx, cy = 610, 330
    for radius, color in [(250, '#0f2c3b'), (190, '#123f52'), (130, '#176378')]:
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=color, width=3)
    draw.ellipse((cx - 92, cy - 92, cx + 92, cy + 92), fill='#102936', outline='#22c7e7', width=5)
    draw.ellipse((cx - 48, cy - 48, cx + 48, cy + 48), fill='#f5fbff', outline='#f6b735', width=6)
    draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill='#22c7e7')

    for x in range(130, 1070, 150):
        draw.line((x, 130, x + 80, 130), fill='#1aa4bd', width=2)
        draw.ellipse((x + 85, 124, x + 97, 136), fill='#f6b735')
    for x in range(170, 1030, 170):
        draw.line((x, 555, x + 100, 555), fill='#f6b735', width=2)
        draw.ellipse((x - 14, 547, x + 2, 563), fill='#22c7e7')

    title_font = font(68, bold=True)
    body_font = font(28)
    draw.text((64, 56), 'AERO A.I', font=title_font, fill='#f7fbff')
    draw.text((68, 138), 'Private local assistant', font=body_font, fill='#91dbea')
    draw.text((68, 606), 'Voice | Web | Files | Memory | Automation', font=body_font, fill='#d8e9ef')

    image.save(path, quality=95)


def draw_feature(path, title, subtitle, accent='#22c7e7'):
    width, height = 1280, 720
    image = Image.new('RGB', (width, height), '#f7f9fb')
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, width, height), fill='#f7f9fb')
    draw.rectangle((0, 0, width, 86), fill='#07365b')
    draw.rectangle((0, height - 24, width, height), fill=accent)

    title_font = font(76, bold=True)
    subtitle_font = font(34)
    small_font = font(24)

    draw.text((72, 150), title, font=title_font, fill='#07365b')
    draw.text((78, 252), subtitle, font=subtitle_font, fill='#536879')
    draw.text((78, 38), 'AERO A.I', font=small_font, fill='#f7fbff')

    cx, cy = 950, 370
    draw.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), outline='#07365b', width=8)
    draw.ellipse((cx - 104, cy - 104, cx + 104, cy + 104), outline=accent, width=10)
    draw.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), fill='#07365b')
    draw.polygon([(cx - 260, cy + 110), (cx - 40, cy + 40), (cx - 112, cy + 100)], fill=accent)
    draw.polygon([(cx - 260, cy + 160), (cx - 28, cy + 78), (cx - 95, cy + 136)], fill='#07365b')
    draw.polygon([(cx - 118, cy - 76), (cx + 182, cy - 260), (cx + 128, cy - 62), (cx + 52, cy - 110)], fill='#f6b735')
    draw.polygon([(cx + 178, cy - 260), (cx + 220, cy - 312), (cx + 198, cy - 128)], fill='#f6b735')

    image.save(path, quality=95)


draw_logo(IMAGE_DIR / 'aero.png')
draw_logo(IMAGE_DIR / 'aero.jpg')
draw_assistant(IMAGE_DIR / 'aero_assistant.png')
draw_feature(IMAGE_DIR / 'face-600x900.png', 'Gesture & Face Vision', 'Private recognition workflows for Aero', '#f6b735')
draw_feature(IMAGE_DIR / 'maxresdefault.jpg', 'Smart News & Web', 'Fresh answers with local-first control', '#22c7e7')
draw_feature(IMAGE_DIR / 'maxresdefault (1).jpg', 'Knowledge Search', 'Wikipedia, web lookup, and summaries', '#8a7146')

print('Wrote Aero images to', IMAGE_DIR)
