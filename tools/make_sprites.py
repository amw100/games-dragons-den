"""
Red Dragon sprite sheet — proper pixel art, 48×48 per frame.
Dragon faces RIGHT. Side-view flying pose.
  - Elongated reptilian head with snout, teeth, slit pupil
  - Gold/amber underbelly
  - Dorsal spines along neck and back
  - Large bat wings (bone fingers + membrane)
  - Spade-tipped tail extending LEFT
  - Taloned legs

Row 0: Flying  — wings-up, mid-up, level, mid-down
Row 1: Death   — hit-flash, tilting, spinning, splat
"""

from PIL import Image, ImageDraw

CELL = 48
GAP  = 2
COLS = 4
ROWS = 2
W = COLS * CELL + (COLS + 1) * GAP
H = ROWS * CELL + (ROWS + 1) * GAP
T = (0, 0, 0, 0)

# ── Red Dragon Palette ────────────────────────────────────────────────────────
BK  = ( 14,   5,  22, 255)   # deep outline
DM  = ( 80,   6,   6, 255)   # deepest maroon shadow
DR  = (138,  16,  16, 255)   # dark red
R   = (192,  34,  34, 255)   # main red body
MR  = (218,  54,  40, 255)   # mid red
LR  = (240,  84,  54, 255)   # bright highlight
OR  = (252, 118,  36, 255)   # orange-red tip
GO  = (194, 138,  14, 255)   # gold belly (dark)
YG  = (240, 198,  46, 255)   # gold belly (bright)
EY  = (244, 192,  10, 255)   # eye amber
EP  = (  8,   4,  16, 255)   # eye pupil (near-black)
WH  = (255, 255, 255, 255)   # white (teeth, eye shine)
WBN = (100,  14,  14, 255)   # wing bone / finger
WMD = (152,  24,  24, 255)   # wing membrane dark
WML = (196,  50,  42, 255)   # wing membrane light
GR  = (144, 128, 140, 255)   # talon grey
GRL = (192, 180, 188, 255)   # talon highlight
# Flash palette
FLB = (252, 210, 180, 255)   # flash body
FLD = (236, 150, 110, 255)   # flash dark


# ── Utility ───────────────────────────────────────────────────────────────────

def add_outline(img):
    """1-px dark outline around all non-transparent, non-outline pixels."""
    src = img.load()
    out = img.copy()
    dst = out.load()
    bk3 = BK[:3]
    for y in range(CELL):
        for x in range(CELL):
            if src[x, y][3] == 0:
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1),
                                (-1,-1),(-1,1),(1,-1),(1,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < CELL and 0 <= ny < CELL:
                        nb = src[nx, ny]
                        if nb[3] > 0 and nb[:3] != bk3:
                            dst[x, y] = BK
                            break
    return out


# ── Wings ─────────────────────────────────────────────────────────────────────

def draw_wings(d, style):
    """
    Bat wings with visible bone fingers and leathery membrane.
    Root attachment ~(18-22, 24). Both wings drawn for visual clarity.
    """
    if style == 'up':
        # Left wing sweeps upper-left
        d.polygon([(20,24),(3,2),(11,0),(20,14),(22,24)],  fill=WML)
        d.polygon([(20,24),(8,4),(15,2),(21,15),(22,24)],  fill=WMD)
        d.line([20,24, 3,2],  fill=WBN, width=2)   # leading finger
        d.line([20,24,11,0],  fill=WBN, width=2)   # mid finger
        d.line([20,24,18,3],  fill=WBN, width=1)   # trailing finger
        # Right wing sweeps upper-right
        d.polygon([(24,24),(24,2),(31,0),(28,14),(26,24)], fill=WML)
        d.polygon([(24,24),(25,4),(30,2),(27,15),(25,24)], fill=WMD)
        d.line([24,24,24,2],  fill=WBN, width=2)
        d.line([24,24,31,0],  fill=WBN, width=2)
        d.line([24,24,28,3],  fill=WBN, width=1)

    elif style == 'mid_up':
        d.polygon([(20,24),(2,8),(9,5),(19,17),(22,24)],   fill=WML)
        d.polygon([(20,24),(5,10),(13,7),(20,18),(22,24)], fill=WMD)
        d.line([20,24, 2,8],  fill=WBN, width=2)
        d.line([20,24, 9,5],  fill=WBN, width=2)
        d.line([20,24,15,7],  fill=WBN, width=1)
        d.polygon([(24,24),(22,8),(29,5),(27,17),(26,24)], fill=WML)
        d.polygon([(24,24),(23,10),(28,7),(26,18),(25,24)],fill=WMD)
        d.line([24,24,22,8],  fill=WBN, width=2)
        d.line([24,24,29,5],  fill=WBN, width=2)
        d.line([24,24,27,7],  fill=WBN, width=1)

    elif style == 'level':
        # Wings fully horizontal — largest silhouette
        d.polygon([(20,25),(0,19),(0,27),(16,30),(20,27)], fill=WML)
        d.polygon([(20,25),(2,21),(0,24),(14,28),(20,27)], fill=WMD)
        d.line([20,25,0,19],  fill=WBN, width=2)
        d.line([20,25,0,27],  fill=WBN, width=1)
        d.line([20,25,1,23],  fill=WBN, width=1)
        d.polygon([(24,25),(44,19),(44,27),(28,30),(24,27)],fill=WML)
        d.polygon([(24,25),(42,21),(44,24),(30,28),(24,27)],fill=WMD)
        d.line([24,25,44,19],  fill=WBN, width=2)
        d.line([24,25,44,27],  fill=WBN, width=1)
        d.line([24,25,43,23],  fill=WBN, width=1)

    elif style == 'mid_down':
        d.polygon([(20,25),(1,36),(0,44),(14,29),(20,27)], fill=WML)
        d.polygon([(20,25),(3,38),(1,36),(12,29),(20,27)], fill=WMD)
        d.line([20,25,1,36],  fill=WBN, width=2)
        d.line([20,25,0,44],  fill=WBN, width=1)
        d.line([20,25,2,40],  fill=WBN, width=1)
        d.polygon([(24,25),(43,36),(44,44),(28,29),(24,27)],fill=WML)
        d.polygon([(24,25),(41,38),(43,36),(29,29),(24,27)],fill=WMD)
        d.line([24,25,43,36],  fill=WBN, width=2)
        d.line([24,25,44,44],  fill=WBN, width=1)
        d.line([24,25,42,40],  fill=WBN, width=1)


# ── Dragon body ───────────────────────────────────────────────────────────────

def draw_dragon_body(d, bc, dc, lc, flash=False):
    """Tail, torso, neck, head, horns, eye, spines, legs."""

    belly_d = GO
    belly_l = YG

    # ── TAIL (spade tip extending left) ───────────────────────────────
    # Thick where it meets the body, tapers to a diamond tip
    d.polygon([(10,28),(10,40),(7,40),(4,37),(2,33),(2,30),(4,27),(8,26)], fill=dc)
    d.polygon([(11,28),(11,39),(8,38),(5,36),(3,33),(3,31),(5,28),(9,27)], fill=bc)
    d.polygon([(11,28),(11,32),(9,31),(7,29),(9,27)],                       fill=lc)
    # Spade / arrowhead tip
    d.polygon([(2,28),(5,23),(8,28),(5,34),(2,31)], fill=dc)
    d.polygon([(3,28),(5,24),(7,28),(5,33),(3,30)], fill=bc)

    # ── TORSO ─────────────────────────────────────────────────────────
    d.ellipse([ 8, 23, 36, 44], fill=dc)    # shadow base
    d.ellipse([ 9, 22, 35, 43], fill=bc)    # main body
    d.ellipse([10, 22, 26, 30], fill=lc)    # dorsal highlight
    d.ellipse([10, 32, 34, 43], fill=belly_d)  # belly (gold, dark)
    d.ellipse([12, 34, 32, 43], fill=belly_l)  # belly highlight

    # ── NECK ──────────────────────────────────────────────────────────
    # Tapers from shoulder (~30,22) up to jaw (~36,12)
    d.polygon([(28,22),(34,10),(40,10),(38,20),(32,26)], fill=dc)
    d.polygon([(29,22),(35,11),(39,11),(37,20),(32,25)], fill=bc)
    d.polygon([(30,22),(35,12),(38,13),(36,20),(32,24)], fill=lc)

    # ── DORSAL SPINES along neck + back ───────────────────────────────
    for sx, sy in [(33,10),(29,16),(25,20),(21,22),(17,23),(13,24)]:
        d.polygon([(sx-3,sy),(sx,sy-6),(sx+3,sy)], fill=dc)
        d.polygon([(sx-2,sy),(sx,sy-4),(sx+2,sy)], fill=lc)

    # ── HEAD ──────────────────────────────────────────────────────────
    # Back of skull — rounded
    d.ellipse([28, 4, 46, 22], fill=dc)
    d.ellipse([28, 4, 45, 21], fill=bc)
    d.ellipse([29, 4, 38, 11], fill=lc)   # skull highlight

    # Upper jaw / snout (long, reptilian)
    d.polygon([(36,13),(47,16),(47,21),(40,21),(36,18)], fill=dc)
    d.polygon([(36,13),(46,16),(46,20),(40,20),(36,17)], fill=bc)
    d.polygon([(37,13),(44,15),(44,17),(37,16)],          fill=lc)

    # Lower jaw (slightly shorter)
    d.polygon([(36,18),(44,20),(42,26),(36,24)], fill=dc)
    d.polygon([(36,18),(43,20),(41,25),(36,23)], fill=bc)

    # Nostril
    d.ellipse([43,15,46,17], fill=dc)

    # Teeth — upper row pointing down
    for tx in [38, 41, 44]:
        d.polygon([(tx-1,20),(tx+1,20),(tx,22)], fill=WH)
    # Lower row pointing up
    for tx in [38, 41]:
        d.polygon([(tx-1,23),(tx+1,23),(tx,21)], fill=WH)

    # ── EYE ───────────────────────────────────────────────────────────
    d.ellipse([35, 6, 44, 14], fill=EY)    # amber iris
    if flash:
        d.ellipse([37, 7, 42, 13], fill=WH)   # flash — wide white eye
    else:
        # Vertical slit pupil (reptilian)
        d.ellipse([38, 6, 41, 14], fill=EP)
        d.ellipse([35, 6, 38,  9], fill=WH)   # eye shine

    # ── HORNS ─────────────────────────────────────────────────────────
    # Main horn (sweeps back)
    d.polygon([(35,4),(40,1),(44,6),(42,11),(38,11)], fill=DR)
    d.polygon([(36,4),(40,2),(43,6),(41,10),(38,10)], fill=LR)
    # Secondary horn
    d.polygon([(33,6),(36,4),(38, 8),(36, 9)], fill=DR)
    d.polygon([(34,6),(36,5),(37, 8),(35, 9)], fill=MR)

    # ── LEGS ──────────────────────────────────────────────────────────
    # Back leg (left)
    d.polygon([(12,40),(16,40),(16,47),(12,47)], fill=dc)
    d.polygon([(13,40),(16,40),(16,47),(13,47)], fill=bc)
    # Back talons
    d.polygon([(10,46),(13,43),(13,48)], fill=GR)
    d.polygon([(13,47),(16,44),(17,48)], fill=GR)
    d.polygon([(16,46),(19,43),(20,47)], fill=GR)

    # Front leg (right)
    d.polygon([(28,40),(32,40),(32,47),(28,47)], fill=dc)
    d.polygon([(29,40),(32,40),(32,47),(29,47)], fill=bc)
    # Front talons
    d.polygon([(26,46),(29,43),(29,48)], fill=GR)
    d.polygon([(29,47),(32,44),(33,48)], fill=GR)
    d.polygon([(32,46),(35,43),(36,47)], fill=GR)


# ── Frame builders ────────────────────────────────────────────────────────────

def make_dragon(wing_style='up', flash=False, dead_eyes=False):
    img = Image.new('RGBA', (CELL, CELL), T)
    d   = ImageDraw.Draw(img)

    if flash:
        bc, dc, lc = FLB, FLD, (255, 230, 200, 255)
    else:
        bc, dc, lc = R, DR, MR

    draw_wings(d, wing_style)
    draw_dragon_body(d, bc, dc, lc, flash=flash)

    if dead_eyes:
        # Override eye with X
        d.ellipse([35, 6, 44, 14], fill=EY)
        d.line([35, 6, 44, 14], fill=BK, width=2)
        d.line([44, 6, 35, 14], fill=BK, width=2)

    return add_outline(img)


def make_splat():
    """Splat frame — flattened dragon with sparkle stars."""
    img = Image.new('RGBA', (CELL, CELL), T)
    d   = ImageDraw.Draw(img)

    # Sparkle stars (8-pointed)
    for sx, sy in [(5,4),(13,2),(23,5),(33,3),(41,6),(45,2)]:
        pts = [(sx,sy-3),(sx-1,sy-1),(sx-3,sy),(sx-1,sy+1),
               (sx,sy+3),(sx+1,sy+1),(sx+3,sy),(sx+1,sy-1)]
        d.polygon(pts, fill=YG)

    # Flattened body strip
    d.rectangle([2, 31, 46, 38], fill=DR)
    d.rectangle([3, 32, 45, 37], fill=R)
    d.rectangle([5, 34, 43, 37], fill=YG)

    # Squished head on the left
    d.ellipse([ 2, 27, 20, 35], fill=DR)
    d.ellipse([ 3, 28, 19, 34], fill=R)

    # X eyes on squished head
    d.line([ 6, 29, 11, 33], fill=BK, width=2)
    d.line([11, 29,  6, 33], fill=BK, width=2)

    # Squished horn
    d.polygon([(10,25),(14,26),(13,28),(10,27)], fill=LR)

    # Tongue lolling out
    d.ellipse([14, 31, 18, 35], fill=(210, 65, 95, 255))

    # Talons splayed below
    for cx in [8, 12, 16, 26, 30, 34, 40]:
        d.polygon([(cx-2,38),(cx,36),(cx+2,38)], fill=GR)

    return add_outline(img)


# ── Assemble sheet ────────────────────────────────────────────────────────────

sheet = Image.new('RGBA', (W, H), T)

# Row 0 — flying
for col, ws in enumerate(['up', 'mid_up', 'level', 'mid_down']):
    frame = make_dragon(wing_style=ws)
    ox = GAP + col * (CELL + GAP)
    sheet.paste(frame, (ox, GAP), frame)

# Row 1 — death
f0 = make_dragon('level', flash=True)                             # hit flash
f1 = make_dragon('mid_up', dead_eyes=True).rotate(               # tilting
         -22, resample=Image.NEAREST, expand=False)
f2 = make_dragon('up', dead_eyes=True).rotate(                   # spinning upside-down
         180, resample=Image.NEAREST, expand=False)
f3 = make_splat()                                                  # splat

for col, frame in enumerate([f0, f1, f2, f3]):
    ox = GAP + col * (CELL + GAP)
    oy = GAP + CELL + GAP
    sheet.paste(frame, (ox, oy), frame)

sheet.save('../assets/dragon/dragon.png')
preview = sheet.resize((W * 4, H * 4), Image.NEAREST)
preview.save('../assets/dragon/dragon_4x.png')

print(f"Saved assets/dragon/dragon.png      ({W}×{H}px  — native)")
print(f"Saved assets/dragon/dragon_4x.png   ({W*4}×{H*4}px — 4× preview)")
print()
print("Row 0 — Flying:  wings-up | mid-up | level | mid-down")
print("Row 1 — Death:   hit-flash | tilting | spinning | splat")
