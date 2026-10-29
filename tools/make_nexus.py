"""Draws the Nexus Mods page images in the mod's amber-on-ink style.
usage: make_nexus.py <out dir>
  00-header.png        2600x744 page header
  01-logo.png          1280x720 (same as the Fluffy card)
  02-whats-unlocked.png 1280x720 skin counts from skins-viewer.bin"""
import os, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from make_screenshot import AMBER, WHITE, SOFT, DIM, INK, background, badge, card, font

out = sys.argv[1]
os.makedirs(out, exist_ok=True)

# Header: badge left, title and tagline.
W, H = 2600, 744
img = background(W, H)
b = badge(400)
img.paste(b, (230, (H - 400) // 2), b)
d = ImageDraw.Draw(img)
x0 = 760
d.text((x0, 176), 'TLOU', font=font('segoeuib.ttf', 58), fill=AMBER)
d.text((x0 - 6, 232), 'Outfit Changer', font=font('segoeuib.ttf', 150), fill=WHITE)
d.rectangle([x0, 452, x0 + 130, 459], fill=AMBER)
d.text((x0, 492), 'Every Joel & Ellie skin  •  no story completion  •  no points spent',
       font=font('segoeui.ttf', 50), fill=SOFT)
img.save(os.path.join(out, '00-header.png'))

card().save(os.path.join(out, '01-logo.png'))

# What's unlocked. Only the Ellie count is given, as counted in the in-game menu
# (1.1.4.0); skins-viewer.bin has more entries than the menu shows.
W, H = 1280, 720
img = background(W, H)
d = ImageDraw.Draw(img)
title = font('segoeuib.ttf', 54)
d.text(((W - d.textlength("What's unlocked", font=title)) / 2, 58), "What's unlocked", font=title, fill=WHITE)
sub = font('segoeui.ttf', 28)
line = 'Every skin in Extras > Skins, owned from the start'
d.text(((W - d.textlength(line, font=sub)) / 2, 138), line, font=sub, fill=SOFT)
tiles = [('33', 'Ellie outfits'), ('All', 'Joel outfits'), ('All', 'Backpacks & hat'),
         ('All', "Ellie's bow"), ('All', "Ellie's pistol"), ('All', "Joel's 9mm & shotgun")]
tw, th, gap = 340, 170, 40
x_start = (W - (3 * tw + 2 * gap)) / 2
for i, (num, label) in enumerate(tiles):
    x = x_start + (i % 3) * (tw + gap)
    y = 230 + (i // 3) * (th + gap)
    d.rounded_rectangle([x, y, x + tw, y + th], radius=18, fill=(30, 40, 60), outline=(52, 64, 88), width=2)
    n = font('segoeuib.ttf', 72)
    d.text((x + (tw - d.textlength(num, font=n)) / 2, y + 18), num, font=n, fill=AMBER)
    lf = font('segoeui.ttf', 28)
    d.text((x + (tw - d.textlength(label, font=lf)) / 2, y + 112), label, font=lf, fill=SOFT)
foot = font('segoeui.ttf', 22)
d.text((W - 40 - d.textlength('TLOU Outfit Changer', font=foot), H - 48), 'TLOU Outfit Changer', font=foot, fill=DIM)
img.save(os.path.join(out, '02-whats-unlocked.png'))
