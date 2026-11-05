# Gera os ícones do app Android a partir do ícone do Evolute (praticantes-icon-1024.png).
# Diferencial: selo verde com batimento no canto, para distinguir do ícone do PWA.
import os, sys
from PIL import Image, ImageDraw
SRC = sys.argv[1]; OUT = sys.argv[2]
src = Image.open(SRC).convert('RGB')
W = src.width / 512.0
BG = src.getpixel((int(256 * W), int(60 * W)))  # cor de fundo do ícone (escuro)
# recorte do "E" + TRAINING
logo = src.crop((int(105 * W), int(95 * W), int(415 * W), int(460 * W)))
def make_fg(S):
    """Camada de frente do ícone adaptativo (canvas S x S, transparente)."""
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    h = int(S * 0.50); w = int(logo.width * h / logo.height)
    lg = logo.resize((w, h), Image.LANCZOS).convert('RGBA')
    # tira o fundo escuro do recorte para a camada ficar transparente fora do desenho
    px = lg.load()
    for y in range(lg.height):
        for x in range(lg.width):
            r, g, b, a = px[x, y]
            d = max(abs(r - BG[0]), abs(g - BG[1]), abs(b - BG[2]))
            if d < 14: px[x, y] = (r, g, b, 0)
            elif d < 40: px[x, y] = (r, g, b, int(255 * (d - 14) / 26))
    im.alpha_composite(lg, (int(S * 0.465 - w / 2), int(S * 0.215)))
    # selo verde com batimento
    cx = cy = int(S * 0.685); r = int(S * 0.075)
    d = ImageDraw.Draw(im)
    d.ellipse((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), fill=BG + (255,))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(34, 197, 94, 255))
    pts = [(-0.70, 0.05), (-0.30, 0.05), (-0.15, -0.55), (0.10, 0.55), (0.25, 0.05), (0.70, 0.05)]
    d.line([(cx + x * r, cy + y * r) for x, y in pts], fill=(255, 255, 255, 255), width=max(2, int(S * 0.016)), joint='curve')
    return im
def legacy(S, round_):
    fg = make_fg(S * 4)  # supersample
    bg = Image.new('RGBA', fg.size, BG + (255,)); bg.alpha_composite(fg)
    # em ícone não adaptativo o desenho ocupa mais: reduz a margem
    bg = bg.crop((int(fg.width * 0.12), int(fg.height * 0.12), int(fg.width * 0.88), int(fg.height * 0.88))).resize((S * 4, S * 4), Image.LANCZOS)
    mask = Image.new('L', bg.size, 0); md = ImageDraw.Draw(mask)
    if round_: md.ellipse((0, 0, bg.width - 1, bg.height - 1), fill=255)
    else: md.rounded_rectangle((0, 0, bg.width - 1, bg.height - 1), radius=int(bg.width * 0.22), fill=255)
    out = Image.new('RGBA', bg.size, (0, 0, 0, 0)); out.paste(bg, (0, 0), mask)
    return out.resize((S, S), Image.LANCZOS)
DENS = {'mdpi': (48, 108), 'hdpi': (72, 162), 'xhdpi': (96, 216), 'xxhdpi': (144, 324), 'xxxhdpi': (192, 432)}
for k, (L, F) in DENS.items():
    d = os.path.join(OUT, 'mipmap-' + k); os.makedirs(d, exist_ok=True)
    legacy(L, False).save(os.path.join(d, 'ic_launcher.png'))
    legacy(L, True).save(os.path.join(d, 'ic_launcher_round.png'))
    make_fg(F).save(os.path.join(d, 'evolute_fg.png'))
v = os.path.join(OUT, 'mipmap-anydpi-v26'); os.makedirs(v, exist_ok=True)
xml = '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/evolute_bg"/>\n    <foreground android:drawable="@mipmap/evolute_fg"/>\n</adaptive-icon>\n'
for n in ('ic_launcher.xml', 'ic_launcher_round.xml'): open(os.path.join(v, n), 'w').write(xml)
vv = os.path.join(OUT, 'values'); os.makedirs(vv, exist_ok=True)
open(os.path.join(vv, 'evolute_colors.xml'), 'w').write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="evolute_bg">#%02x%02x%02x</color>\n</resources>\n' % BG)
print('ok, fundo', BG)
