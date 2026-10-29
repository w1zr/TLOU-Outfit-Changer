"""Draws the mod's artwork: an amber badge with a clothes hanger, on ink blue.
usage: make_screenshot.py <out dir>
  screenshot.png  1280x720 Fluffy Mod Manager preview (ideal size per Fluffy's readme)
  logo.png        512x512 logo, transparent background (README, Nexus, GitHub)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

INK, INK_DEEP = (22, 30, 46), (12, 17, 27)
AMBER, AMBER_DARK = (232, 163, 61), (196, 124, 34)
WHITE, SOFT, DIM = (240, 236, 228), (178, 186, 202), (116, 128, 150)
SS = 4  # supersampling for smooth edges


def badge(size):
    """Amber disc with a ring and a hanger in ink, transparent outside."""
    S = size * SS
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, S - 1, S - 1], fill=AMBER)
    ring = S * 0.035
    d.ellipse([ring * 1.6, ring * 1.6, S - ring * 1.6, S - ring * 1.6], outline=AMBER_DARK, width=round(ring * 0.5))

    u = S / 300                 # drawing units: the badge is 300 across
    st = round(13 * u)          # stroke
    def p(x, y): return (S / 2 + x * u, S / 2 + y * u)
    def dot(x, y): d.ellipse([x - st / 2, y - st / 2, x + st / 2, y + st / 2], fill=INK)
    r, hy0 = 24, -42            # hook: 3/4 circle opening to the lower left, then the neck
    hx, hy = p(0, hy0)
    # PIL draws arc strokes inward from the bounding box, so pad by half a stroke.
    pad = st / 2
    d.arc([hx - r * u - pad, hy - r * u - pad, hx + r * u + pad, hy + r * u + pad], 180, 450, fill=INK, width=st)
    d.line([p(0, hy0 + r), p(0, 0)], fill=INK, width=st)
    dot(*p(-r, hy0)); dot(*p(0, hy0 + r))  # round the tip and the hook/neck join
    pts = [p(0, 0), p(100, 62), p(-100, 62), p(0, 0)]  # shoulders and bar
    d.line(pts, fill=INK, width=st, joint='curve')
    for x, y in pts[:3]: dot(x, y)
    return img.resize((size, size), Image.LANCZOS)


def font(name, size):
    return ImageFont.truetype('C:/Windows/Fonts/' + name, size)


out = sys.argv[1]

# Fluffy preview card: diagonal ink gradient, badge left, text left-aligned.
W, H = 1280, 720
card = Image.new('RGB', (W, H))
px = card.load()
for y in range(H):
    for x in range(0, W, 4):
        t = min(1, (x / W) * 0.6 + (y / H) * 0.6)
        c = tuple(round(a + (b - a) * t) for a, b in zip(INK, INK_DEEP))
        for k in range(4): px[x + k, y] = c
b = badge(300)
card.paste(b, (110, (H - 300) // 2), b)
d = ImageDraw.Draw(card)
x0 = 470
d.text((x0, 222), 'TLOU', font=font('segoeuib.ttf', 40), fill=AMBER)
d.text((x0 - 4, 262), 'Outfit Changer', font=font('segoeuib.ttf', 84), fill=WHITE)
d.rectangle([x0, 386, x0 + 90, 391], fill=AMBER)
body = font('segoeui.ttf', 30)
d.text((x0, 418), 'Every Joel & Ellie skin, on any save', font=body, fill=SOFT)
d.text((x0, 458), 'No story completion. No points spent.', font=body, fill=SOFT)
d.text((x0, 520), 'Extras > Skins  \u00b7  in-game Skins menu', font=font('segoeui.ttf', 24), fill=DIM)
card.save(os.path.join(out, 'screenshot.png'))

# Square logo: just the badge.
badge(512).save(os.path.join(out, 'logo.png'))
