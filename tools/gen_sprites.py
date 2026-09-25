#!/usr/bin/env python3
"""Procedural pixel-art generator for the Coin Collector game (Godot 4).

Creates all sprite PNGs under game/assets/sprites/ :
  - player skin idle/walk/run animation strips + jump frames
  - coin spin strips (gold, snowflake-coin, shell-coin)
  - slime enemies (blue / icy / sandy) idle+hop strips
  - tilesets (grass/dirt, snow, sand) and background deco
  - UI icons and particles
Run:  python3 tools/gen_sprites.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "game", "assets", "sprites")

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def new(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)


def rect(img, x0, y0, x1, y1, c):
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=c)


def circle(img, cx, cy, r, c):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)


def outline(img, color):
    """Add a 1px outline around every non-transparent pixel."""
    w, h = img.size
    src = img.load()
    out = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    o = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] > 0:
                o[x + 1, y + 1] = src[x, y]
    res = new(w, h)
    r = res.load()
    for y in range(h + 2):
        for x in range(w + 2):
            if o[x, y][3] == 0:
                # check neighbours for filled pixel -> outline
                nb = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                for nx, ny in nb:
                    if 0 <= nx < w + 2 and 0 <= ny < h + 2 and o[nx, ny][3] > 0:
                        gx, gy = x - 1, y - 1
                        if 0 <= gx < w and 0 <= gy < h:
                            r[gx, gy] = color
                        break
    res.paste(out.crop((1, 1, w + 1, h + 1)), (0, 0), out.crop((1, 1, w + 1, h + 1)))
    return res


def save(img, path):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    img.save(full)
    print("wrote", path)


def strip(frames, pad=0):
    """join frames horizontally into one strip"""
    w = sum(f.width for f in frames) + pad * (len(frames) - 1)
    h = max(f.height for f in frames)
    s = new(w, h)
    x = 0
    for f in frames:
        s.paste(f, (x, 0), f)
        x += f.width + pad
    return s


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (c[3],)


# ----------------------------------------------------------------------------
# palette
# ----------------------------------------------------------------------------
SKIN = (247, 208, 160, 255)
SKIN_D = (214, 168, 120, 255)
HAIR_B = (60, 40, 28, 255)
HAIR_G = (90, 170, 70, 255)
HAIR_P = (200, 90, 160, 255)
EYE = (30, 30, 45, 255)
OUTL = (24, 20, 32, 255)

# skins: (name, shirt, pants, shoe, hair, hat_color or None)
SKINS = [
    ("hero",   (220, 60, 60, 255),  (60, 80, 160, 255),  (90, 60, 40, 255), HAIR_B, None),
    ("ninja",  (40, 40, 50, 255),   (25, 25, 35, 255),   (15, 15, 20, 255), HAIR_B, (200, 60, 60, 255)),
    ("explorer",(150, 130, 70, 255),(90, 80, 50, 255),   (70, 50, 30, 255), HAIR_B, (120, 100, 55, 255)),
    ("yeti",   (235, 240, 250, 255),(200, 210, 230, 255),(120, 130, 150,255), (180,200,230,255), None),
    ("surfer", (250, 200, 60, 255), (60, 170, 200, 255), (240, 220, 180,255), HAIR_G, None),
    ("robot",  (150, 160, 175, 255),(100, 110, 125, 255),(70, 75, 90, 255),  (190, 200, 215,255), (250, 90, 90, 255)),
]


# ----------------------------------------------------------------------------
# player character (16x20 per frame)
# ----------------------------------------------------------------------------

def draw_player(skin, pose):
    """pose: dict with leg offsets & arm swing; returns 16x20 image"""
    shirt, pants, shoes, hair, hat = skin[1], skin[2], skin[3], skin[4], skin[5]
    body_dark = shade(shirt, 0.75)
    img = new(16, 20)

    ll, lr = pose.get("legs", (0, 0))     # leg lift amounts
    sw = pose.get("swing", 0)             # arm swing
    bob = pose.get("bob", 0)              # vertical squash
    y0 = 1 + bob

    # legs
    rect(img, 5, 14 + y0, 6, 18 - ll + y0, pants)
    rect(img, 9, 14 + y0, 10, 18 - lr + y0, pants)
    rect(img, 5, 18 - ll + y0, 6, 19 - ll + y0, shoes)
    rect(img, 9, 18 - lr + y0, 10, 19 - lr + y0, shoes)
    # torso
    rect(img, 4, 8 + y0, 11, 14 + y0, shirt)
    rect(img, 4, 13 + y0, 11, 14 + y0, body_dark)
    # arms
    rect(img, 2, 9 + y0 - sw, 3, 13 + y0 - sw, shirt)
    rect(img, 12, 9 + y0 + sw, 13, 13 + y0 + sw, shirt)
    px(img, 2, 13 + y0 - sw, SKIN_D); px(img, 3, 13 + y0 - sw, SKIN_D)
    px(img, 12, 13 + y0 + sw, SKIN_D); px(img, 13, 13 + y0 + sw, SKIN_D)
    # head
    rect(img, 4, 1 + y0, 11, 7 + y0, SKIN)
    rect(img, 4, 6 + y0, 11, 7 + y0, SKIN_D)
    # hair
    rect(img, 4, 1 + y0, 11, 2 + y0, hair)
    rect(img, 4, 1 + y0, 4, 4 + y0, hair)
    rect(img, 11, 1 + y0, 11, 3 + y0, hair)
    # eyes
    px(img, 6, 4 + y0, EYE); px(img, 9, 4 + y0, EYE)
    # mouth
    rect(img, 7, 6 + y0, 8, 6 + y0, (180, 90, 90, 255))
    # hat
    if hat:
        rect(img, 3, 0 + y0, 12, 1 + y0, hat)
        rect(img, 5, -1 + y0 if y0 else 0, 10, 0, hat)
    if skin[0] == "robot":
        px(img, 7, 0 + y0, (255, 250, 120, 255)); px(img, 8, 0 + y0, (255, 250, 120, 255))
    if skin[0] == "yeti":
        rect(img, 4, 3 + y0, 11, 3 + y0, shade(hair, 0.9))
    return outline(img, OUTL)


PLAYER_POSES = {
    "idle": [dict(bob=0), dict(bob=1)],
    "walk": [dict(legs=(2, 0), swing=1),
             dict(legs=(0, 0), swing=0),
             dict(legs=(0, 2), swing=-1),
             dict(legs=(0, 0), swing=0)],
    "run": [dict(legs=(3, 0), swing=2, bob=0),
            dict(legs=(0, 0), swing=0, bob=1),
            dict(legs=(0, 3), swing=-2, bob=0),
            dict(legs=(0, 0), swing=0, bob=1)],
    "jump": [dict(legs=(1, 2), swing=2), dict(legs=(2, 1), swing=2)],
}


def gen_players():
    for skin in SKINS:
        name = skin[0]
        for anim, poses in PLAYER_POSES.items():
            frames = [draw_player(skin, p) for p in poses]
            save(strip(frames), f"player/{name}_{anim}.png")


# ----------------------------------------------------------------------------
# coins (12x12 spin, 6 frames)
# ----------------------------------------------------------------------------

def draw_coin(cx, cy, edge, hi, shine, w_frac, sym=None):
    img = new(12, 12)
    rw = max(2, int(round(5 * w_frac)))
    for y in range(-5, 6):
        rr = int(round(5 * (1 - (abs(y) / 5.5) ** 2) ** 0.5))
        rr = min(rr, 5)
        half = max(1, int(round(rr * w_frac)))
        rect(img, 6 - half, 6 + y, 6 + half, 6 + y, edge)
    # face
    for y in range(-4, 5):
        rr = int(round(4 * (1 - (abs(y) / 5.0) ** 2) ** 0.5))
        half = max(0, int(round(rr * w_frac)))
        if half:
            rect(img, 6 - half, 6 + y, 6 + half, 6 + y, cy)
    # highlight
    rect(img, 6 - max(1, int(2 * w_frac)), 3, 6 - max(1, int(1 * w_frac)), 5, hi)
    px(img, 6, 2, shine)
    if sym and w_frac > 0.7:
        rect(img, 5, 4, 6, 4, edge); rect(img, 5, 7, 6, 7, edge)
        px(img, 5, 5, edge); px(img, 6, 6, edge)
    return outline(img, OUTL)


def gen_coins():
    sets = {
        "gold":  ((252, 214, 80, 255), (255, 244, 170, 255), (255, 255, 255, 255), (190, 140, 20, 255)),
        "snow":  ((170, 220, 255, 255), (235, 250, 255, 255), (255, 255, 255, 255), (90, 140, 200, 255)),
        "shell": ((250, 190, 140, 255), (255, 235, 210, 255), (255, 255, 255, 255), (200, 120, 80, 255)),
    }
    widths = [1.0, 0.75, 0.45, 0.2, 0.45, 0.75]
    for name, (cy, hi, shine, edge) in sets.items():
        frames = [draw_coin(cy, edge, edge, hi, shine, w, sym=(name == "gold")) for w in widths]
        save(strip(frames), f"coins/{name}_spin.png")
    # big gem pickup 14x14
    g = new(14, 14)
    d = ImageDraw.Draw(g)
    d.polygon([(7, 1), (12, 5), (7, 13), (2, 5)], fill=(120, 220, 255, 255), outline=OUTL)
    d.polygon([(7, 1), (9, 5), (7, 13)], fill=(190, 245, 255, 255))
    d.polygon([(7, 1), (5, 5), (7, 13)], fill=(80, 160, 230, 255))
    save(outline(g, OUTL), "coins/gem.png")


# ----------------------------------------------------------------------------
# slimes (16x12 frames: squish cycle)
# ----------------------------------------------------------------------------

def draw_slime(body, dark, eye_c, acc=None):
    imgs = []
    for i, (sx, sy) in enumerate([(1.0, 1.0), (1.12, 0.85), (1.0, 1.0), (0.88, 1.12)]):
        img = new(16, 14)
        w = int(12 * sx); h = int(9 * sy)
        x0 = 8 - w // 2; y1 = 13; y0 = y1 - h
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x0, y0, x0 + w, y1], radius=max(2, h // 3), fill=body, outline=OUTL)
        # bottom shading
        d.rectangle([x0 + 1, y1 - 2, x0 + w - 1, y1 - 1], fill=dark)
        # top shine
        px(img, x0 + 3, y0 + 2, (255, 255, 255, 200))
        px(img, x0 + 4, y0 + 2, (255, 255, 255, 160))
        # eyes
        ex = max(x0 + 2, 8 - w // 4 - 1)
        ey = y0 + max(2, h // 3)
        rect(img, ex, ey, ex + 1, ey + 2, (255, 255, 255, 255))
        rect(img, 15 - ex - 1, ey, 15 - ex, ey + 2, (255, 255, 255, 255))
        px(img, ex, ey + 1, eye_c); px(img, 15 - ex, ey + 1, eye_c)
        # mouth
        rect(img, 7, ey + 3, 8, ey + 3, dark)
        if acc == "ice":
            d.polygon([(x0 + w - 2, y0 - 2), (x0 + w + 1, y0 - 2), (x0 + w - 1, y0 + 2)],
                      fill=(200, 240, 255, 255), outline=OUTL)
        if acc == "sand":
            px(img, x0 + 2, y0, (250, 230, 160, 255)); px(img, x0 + w - 3, y0 + 1, (250, 230, 160, 255))
        if acc == "crown":
            rect(img, 6, y0 - 2, 9, y0 - 1, (252, 214, 80, 255))
            px(img, 6, y0 - 3, (252, 214, 80, 255)); px(img, 9, y0 - 3, (252, 214, 80, 255))
        imgs.append(img)
    return imgs


def gen_enemies():
    save(strip(draw_slime((90, 190, 90, 255), (50, 130, 50, 255), EYE)),
         "enemies/slime_green_hop.png")
    save(strip(draw_slime((150, 210, 250, 255), (90, 150, 210, 255), EYE, "ice")),
         "enemies/slime_ice_hop.png")
    save(strip(draw_slime((240, 200, 120, 255), (190, 150, 70, 255), EYE, "sand")),
         "enemies/slime_sand_hop.png")
    save(strip(draw_slime((230, 80, 80, 255), (160, 40, 40, 255), (255, 240, 80, 255), "crown")),
         "enemies/slime_king_hop.png")
    # bat 14x10 flap strip (4)
    frames = []
    for wing in [(0, -2), (0, 0), (0, 2), (0, 0)]:
        img = new(16, 12)
        body = (80, 60, 100, 255)
        rect(img, 6, 4, 9, 8, body)
        px(img, 7, 5, (255, 80, 80, 255)); px(img, 8, 5, (255, 80, 80, 255))
        wy = 4 + wing[1]
        d = ImageDraw.Draw(img)
        d.polygon([(6, wy + 2), (1, wy), (2, wy + 4)], fill=shade(body, 0.8), outline=OUTL)
        d.polygon([(9, wy + 2), (14, wy), (13, wy + 4)], fill=shade(body, 0.8), outline=OUTL)
        frames.append(outline(img, OUTL))
    save(strip(frames), "enemies/bat_fly.png")


# ----------------------------------------------------------------------------
# tiles & backgrounds (16x16 seamless-ish)
# ----------------------------------------------------------------------------

def noise_fill(img, base, variants, seed):
    import random
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, img.width - 1, img.height - 1], fill=base)
    for _ in range(int(img.width * img.height * 0.18)):
        x = rnd.randrange(img.width); y = rnd.randrange(img.height)
        d.point((x, y), fill=rnd.choice(variants))


def gen_tiles():
    grass = new(16, 16); noise_fill(grass, (70, 150, 60, 255),
                                    [(58, 130, 50, 255), (86, 168, 72, 255), (100, 185, 80, 255)], 1)
    for x in range(0, 16, 3):
        px(grass, x, 0, (110, 200, 90, 255)); px(grass, x + 1, 1, (95, 180, 80, 255))
    save(grass, "tiles/grass.png")

    dirt = new(16, 16); noise_fill(dirt, (120, 82, 52, 255),
                                   [(100, 68, 42, 255), (140, 96, 62, 255)], 2)
    save(dirt, "tiles/dirt.png")

    snow = new(16, 16); noise_fill(snow, (238, 244, 252, 255),
                                   [(222, 232, 246, 255), (250, 252, 255, 255)], 3)
    save(snow, "tiles/snow.png")

    ice = new(16, 16); noise_fill(ice, (160, 210, 245, 255),
                                  [(140, 195, 235, 255), (200, 235, 255, 255)], 4)
    save(ice, "tiles/ice.png")

    sand = new(16, 16); noise_fill(sand, (238, 214, 150, 255),
                                   [(222, 198, 132, 255), (250, 230, 170, 255)], 5)
    save(sand, "tiles/sand.png")

    water = new(16, 16); noise_fill(water, (60, 130, 210, 255),
                                    [(45, 110, 190, 255), (90, 160, 235, 255)], 6)
    for x in range(0, 16, 4):
        rect(water, x, 4, x + 2, 4, (150, 200, 250, 255))
        rect(water, x + 2, 11, x + 4, 11, (150, 200, 250, 255))
    save(water, "tiles/water.png")

    stone = new(16, 16); noise_fill(stone, (110, 110, 125, 255),
                                    [(90, 90, 105, 255), (135, 135, 150, 255)], 7)
    save(stone, "tiles/stone.png")

    # brick platform variants (16x16 with top edge highlight)
    for name, top, bot in [("grass_top", (110, 200, 90, 255), (120, 82, 52, 255)),
                           ("snow_top", (250, 252, 255, 255), (150, 170, 200, 255)),
                           ("sand_top", (250, 230, 170, 255), (200, 160, 100, 255))]:
        t = new(16, 16)
        noise_fill(t, bot, [shade(bot, 0.85), shade(bot, 1.15)], 11)
        rect(t, 0, 0, 15, 3, top)
        rect(t, 0, 0, 15, 0, shade(top, 1.2))
        for x in range(0, 16, 4):
            px(t, x, 3, shade(top, 0.7))
        save(t, f"tiles/{name}.png")


def gen_deco():
    # pine tree 24x32
    p = new(24, 32)
    d = ImageDraw.Draw(p)
    rect(p, 10, 26, 13, 31, (110, 70, 40, 255))
    d.polygon([(12, 0), (22, 12), (2, 12)], fill=(40, 110, 60, 255), outline=OUTL)
    d.polygon([(12, 6), (23, 19), (1, 19)], fill=(48, 130, 70, 255), outline=OUTL)
    d.polygon([(12, 13), (24, 27), (0, 27)], fill=(56, 145, 78, 255), outline=OUTL)
    save(p, "deco/pine.png")
    # snowy pine
    sp = p.copy()
    d = ImageDraw.Draw(sp)
    d.polygon([(12, 0), (18, 7), (6, 7)], fill=(240, 248, 255, 255))
    d.polygon([(12, 13), (19, 21), (5, 21)], fill=(240, 248, 255, 230))
    save(sp, "deco/pine_snow.png")
    # palm tree 28x36
    pa = new(28, 36)
    d = ImageDraw.Draw(pa)
    d.line([(14, 35), (16, 14), (14, 10)], fill=(140, 95, 55, 255), width=3)
    for ang in range(0, 360, 45):
        import math
        x2 = 14 + int(11 * math.cos(math.radians(ang)))
        y2 = 9 + int(7 * math.sin(math.radians(ang)))
        d.line([(14, 9), (x2, y2)], fill=(60, 160, 70, 255), width=2)
    circle(pa, 12, 12, 2, (120, 80, 40, 255)); circle(pa, 17, 12, 2, (120, 80, 40, 255))
    save(outline(pa, OUTL), "deco/palm.png")
    # cactus 14x24
    c = new(14, 24)
    rect(c, 5, 2, 8, 23, (70, 150, 70, 255))
    rect(c, 0, 8, 3, 11, (70, 150, 70, 255)); rect(c, 1, 4, 2, 10, (70, 150, 70, 255))
    rect(c, 10, 6, 13, 9, (70, 150, 70, 255)); rect(c, 11, 2, 12, 8, (70, 150, 70, 255))
    rect(c, 5, 2, 6, 23, (95, 175, 90, 255))
    px(c, 6, 6, (250, 120, 160, 255))
    save(outline(c, OUTL), "deco/cactus.png")
    # rocks
    for n, col in [("rock", (130, 130, 145, 255)), ("rock_snow", (200, 215, 235, 255))]:
        r = new(16, 12)
        d = ImageDraw.Draw(r)
        d.polygon([(2, 11), (4, 3), (10, 1), (14, 6), (13, 11)], fill=col, outline=OUTL)
        d.polygon([(4, 3), (10, 1), (8, 6)], fill=shade(col, 1.2))
        save(r, f"deco/{n}.png")
    # flowers / shells / icicles
    f = new(8, 8)
    circle(f, 4, 3, 2, (250, 90, 90, 255)); px(f, 4, 3, (255, 230, 90, 255))
    rect(f, 4, 5, 4, 7, (60, 140, 60, 255)); px(f, 3, 6, (80, 170, 80, 255))
    save(f, "deco/flower.png")
    sh = new(10, 8)
    d = ImageDraw.Draw(sh)
    d.pieslice([0, 0, 9, 14], 180, 360, fill=(250, 200, 190, 255), outline=OUTL)
    for x in (2, 4, 6):
        d.line([(5, 7), (x, 1)], fill=(220, 140, 130, 255))
    save(sh, "deco/shell.png")
    star = new(10, 10)
    d = ImageDraw.Draw(star)
    d.polygon([(5, 0), (6, 4), (10, 5), (6, 6), (5, 10), (4, 6), (0, 5), (4, 4)],
              fill=(255, 240, 140, 255), outline=OUTL)
    save(star, "deco/star.png")
    # signpost
    s = new(16, 20)
    rect(s, 7, 8, 9, 19, (120, 80, 45, 255))
    rect(s, 1, 2, 15, 9, (170, 120, 70, 255))
    rect(s, 2, 3, 14, 8, (200, 155, 95, 255))
    rect(s, 4, 5, 12, 6, (90, 60, 30, 255))
    save(outline(s, OUTL), "deco/sign.png")
    # igloo 32x20
    ig = new(32, 20)
    d = ImageDraw.Draw(ig)
    d.pieslice([0, 0, 31, 38], 180, 360, fill=(235, 242, 250, 255), outline=OUTL)
    d.rectangle([0, 18, 31, 19], fill=(210, 220, 235, 255))
    d.pieslice([11, 10, 21, 20], 180, 360, fill=(150, 170, 195, 255), outline=OUTL)
    for yy in (6, 11):
        for xx in range(2, 30, 6):
            d.line([(xx, yy), (xx + 4, yy)], fill=(200, 212, 228, 255))
    save(ig, "deco/igloo.png")
    # beach hut 28x24
    bh = new(28, 24)
    d = ImageDraw.Draw(bh)
    d.polygon([(14, 0), (27, 10), (1, 10)], fill=(230, 90, 80, 255), outline=OUTL)
    d.rectangle([4, 10, 23, 23], fill=(250, 240, 210, 255), outline=OUTL)
    d.rectangle([12, 14, 16, 23], fill=(150, 100, 60, 255))
    d.rectangle([6, 13, 10, 16], fill=(140, 210, 240, 255), outline=OUTL)
    save(bh, "deco/hut.png")
    # cloud 24x10
    cl = new(24, 10)
    circle(cl, 6, 6, 4, (255, 255, 255, 235))
    circle(cl, 12, 4, 5, (255, 255, 255, 245))
    circle(cl, 18, 6, 4, (255, 255, 255, 235))
    rect(cl, 4, 6, 20, 9, (255, 255, 255, 240))
    save(cl, "deco/cloud.png")
    # snowflake small
    sf = new(8, 8)
    d = ImageDraw.Draw(sf)
    for ang in range(0, 180, 60):
        import math
        dx = int(round(3 * math.cos(math.radians(ang))))
        dy = int(round(3 * math.sin(math.radians(ang))))
        d.line([(4 - dx, 4 - dy), (4 + dx, 4 + dy)], fill=(220, 240, 255, 255))
    save(sf, "deco/snowflake.png")
    # torch / lamp post
    lp = new(10, 24)
    rect(lp, 4, 6, 5, 23, (70, 70, 85, 255))
    rect(lp, 2, 2, 7, 7, (110, 110, 130, 255))
    rect(lp, 3, 3, 6, 6, (255, 200, 90, 255))
    px(lp, 4, 4, (255, 240, 160, 255))
    save(lp, "deco/lamp.png")


# ----------------------------------------------------------------------------
# UI & particles
# ----------------------------------------------------------------------------

def gen_ui():
    # heart 12x11
    h = new(12, 11)
    d = ImageDraw.Draw(h)
    d.polygon([(6, 10), (1, 5), (1, 2), (3, 0), (6, 2), (9, 0), (11, 2), (11, 5)],
              fill=(235, 60, 70, 255), outline=OUTL)
    px(h, 3, 3, (255, 160, 165, 255)); px(h, 4, 2, (255, 160, 165, 255))
    save(h, "ui/heart.png")
    hd = h.copy(); hd = hd.convert("RGBA")
    d = ImageDraw.Draw(hd)
    d.polygon([(6, 10), (1, 5), (1, 2), (3, 0), (6, 2), (9, 0), (11, 2), (11, 5)],
              fill=(70, 60, 75, 255), outline=(40, 35, 45, 255))
    save(hd, "ui/heart_empty.png")
    # coin ui icon (reuse small gold)
    ci = draw_coin((252, 214, 80, 255), (190, 140, 20, 255), (190, 140, 20, 255),
                   (255, 244, 170, 255), (255, 255, 255, 255), 1.0, sym=True)
    save(ci, "ui/coin_icon.png")
    # lock icon
    lk = new(12, 14)
    d = ImageDraw.Draw(lk)
    d.arc([2, 0, 9, 8], 180, 360, fill=(160, 160, 175, 255), width=2)
    d.rounded_rectangle([1, 5, 10, 13], radius=2, fill=(190, 190, 205, 255), outline=OUTL)
    px(lk, 5, 9, (80, 80, 95, 255)); px(lk, 6, 9, (80, 80, 95, 255))
    save(lk, "ui/lock.png")
    # sparkle particle 8x8 frames
    frames = []
    for r, a in [(3, 255), (2, 200), (1, 140)]:
        im = new(8, 8)
        d = ImageDraw.Draw(im)
        d.polygon([(4, 4 - r - 1), (4 + r // 2 + 1, 4), (4, 4 + r + 1), (4 - r // 2 - 1, 4)],
                  fill=(255, 250, 180, a))
        frames.append(im)
    save(strip(frames), "ui/sparkle.png")
    # dust puff 10x6 frames
    frames = []
    import random
    rnd = random.Random(9)
    for i in range(4):
        im = new(12, 8)
        n = 6 + i * 2
        col = (220, 215, 205, 230 - i * 55)
        for _ in range(n):
            x = rnd.randrange(2, 10); y = rnd.randrange(1, 7)
            px(im, x, y, col)
        frames.append(im)
    save(strip(frames), "ui/dust.png")
    # splash 10x8 frames
    frames = []
    for i in range(4):
        im = new(12, 10)
        d = ImageDraw.Draw(im)
        spread = 2 + i * 2
        col = (150, 200, 250, 240 - i * 55)
        d.line([(6 - spread, 8 - i), (6 - spread - 1, 5 - i)], fill=col)
        d.line([(6 + spread, 8 - i), (6 + spread + 1, 5 - i)], fill=col)
        d.point((6, 3 - i), fill=col)
        frames.append(im)
    save(strip(frames), "ui/splash.png")
    # title logo coin 48x48
    t = new(48, 48)
    d = ImageDraw.Draw(t)
    d.ellipse([2, 2, 45, 45], fill=(190, 140, 20, 255), outline=OUTL, width=2)
    d.ellipse([6, 6, 41, 41], fill=(252, 214, 80, 255))
    d.ellipse([6, 6, 41, 30], fill=(255, 236, 150, 255))
    d.rectangle([20, 12, 27, 15], fill=(190, 140, 20, 255))
    d.rectangle([20, 32, 27, 35], fill=(190, 140, 20, 255))
    d.rectangle([22, 15, 25, 32], fill=(190, 140, 20, 255))
    save(t, "ui/logo_coin.png")


# ----------------------------------------------------------------------------

if __name__ == "__main__":
    gen_players()
    gen_coins()
    gen_enemies()
    gen_tiles()
    gen_deco()
    gen_ui()
    print("sprite generation complete")
