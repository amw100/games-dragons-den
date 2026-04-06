"""
Dragon's Den — Level/environment asset generator.

  assets/level/ceiling_tile.png  — tileable dungeon stone block (ceiling body)
  assets/level/ceiling_edge.png  — bottom face of ceiling with stalactites

Both tile seamlessly horizontally.
Convention matches make_sprites.py / make_obstacles.py.
"""

from PIL import Image, ImageDraw

CELL = 48
GAP  = 2
T    = (0, 0, 0, 0)
BK   = (14,  5, 22, 255)

# ── Dungeon stone palette (cool grey-purple, contrasts warm lava floor) ───────
ST_DK  = (18,  16,  24, 255)   # deep shadow
ST_MD  = (44,  40,  54, 255)   # main stone
ST_LT  = (72,  66,  84, 255)   # lighter face
ST_HL  = (100, 92, 114, 255)   # specular chip
ST_CR  = (28,  24,  36, 255)   # crack line
IR_DK  = ( 28,  26,  30, 255)  # iron deep shadow
IR_MD  = ( 58,  54,  62, 255)  # iron bolt
IR_LT  = ( 96,  90, 102, 255)  # iron face
IR_HL  = (148, 144, 152, 255)  # iron sheen / bolt shine
IR_RST = ( 72,  38,  18, 255)  # rust accent
MO_DK  = (38,  60,  32, 255)   # moss dark
MO_LT  = (62,  96,  50, 255)   # moss light
WD     = (80, 118, 160, 255)   # water drop
WD_HL  = (140, 178, 215, 255)  # water drop highlight

# ── Torch palette ─────────────────────────────────────────────────────────────
WD_BR  = ( 90,  58,  24, 255)  # wood brown
WD_DK  = ( 58,  36,  12, 255)  # wood dark
FL_HT  = (252, 220,  60, 255)  # flame hot centre
FL_MD  = (240, 110,  20, 255)  # flame mid orange
FL_DK  = (170,  40,   8, 255)  # flame dark base
FL_GLW = (255, 200,  80, 128)  # soft outer glow (semi-transparent)


# ── Utility ───────────────────────────────────────────────────────────────────

def add_outline(img):
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


def save_single(img, path):
    sz = CELL + 2 * GAP
    sheet = Image.new('RGBA', (sz, sz), T)
    sheet.paste(img, (GAP, GAP), img)
    sheet.save(path)
    preview = path.replace('.png', '_4x.png')
    sheet.resize((sz * 4, sz * 4), Image.NEAREST).save(preview)
    print(f"Saved {path}  ({sz}×{sz}px)")
    print(f"Saved {preview}  ({sz*4}×{sz*4}px)")


# ═══════════════════════════════════════════════════════════════════════════════
#  CEILING TILE — tileable stone block for the solid ceiling body
# ═══════════════════════════════════════════════════════════════════════════════

# Stone facet polygons (give the impression of cut dungeon blocks)
TILE_FACETS = [
    [(1, 1),(20, 0),(22, 9),(3, 11)],
    [(24, 0),(44, 1),(46, 11),(26, 10)],
    [(0, 18),(14, 16),(16, 28),(0, 30)],
    [(18, 17),(38, 16),(40, 28),(20, 29)],
    [(2, 34),(22, 32),(20, 44),(0, 46)],
    [(26, 33),(46, 34),(47, 44),(28, 43)],
]

# Block mortar lines (horizontal seams between stone rows)
MORTAR_Y = [15, 31]
MORTAR_X = [23]   # vertical seam offset alternates per row

# Iron bolt positions (studs holding the stonework)
BOLT_POS = [(6, 6), (41, 5), (12, 38), (38, 40)]

# Moss cluster positions (bottom edges of stones, where damp collects)
MOSS_POS = [(8, 44), (28, 46), (44, 42)]

# Crack paths (list of (x,y) waypoints)
CRACKS = [
    [(11, 0),(13, 9),(9, 18),(12, 28)],
    [(32, 2),(30, 12),(34, 22),(32, 32),(30, 44)],
]


def make_ceiling_tile():
    img = Image.new('RGBA', (CELL, CELL), T)
    d   = ImageDraw.Draw(img)
    px  = img.load()

    # Base stone fill
    d.rectangle([0, 0, CELL-1, CELL-1], fill=ST_MD)

    # Facets (lighter stone faces)
    for pts in TILE_FACETS:
        d.polygon(pts, fill=ST_LT)
        d.line([pts[0], pts[1]], fill=ST_HL, width=1)   # top highlight edge

    # Mortar / block seams
    for y in MORTAR_Y:
        d.line([(0, y), (CELL-1, y)], fill=ST_DK, width=2)
    for x in MORTAR_X:
        d.line([(x, 0), (x, MORTAR_Y[0]-1)],       fill=ST_DK, width=2)
        d.line([(x+12, MORTAR_Y[0]+2), (x+12, MORTAR_Y[1]-1)], fill=ST_DK, width=2)
        d.line([(x, MORTAR_Y[1]+2), (x, CELL-1)],  fill=ST_DK, width=2)

    # Cracks
    for path in CRACKS:
        for i in range(len(path) - 1):
            d.line([path[i], path[i+1]], fill=ST_CR, width=1)

    # Iron bolts (embedded studs)
    for bx, by in BOLT_POS:
        d.ellipse([bx-3, by-3, bx+3, by+3], fill=IR_MD)
        d.ellipse([bx-1, by-2, bx+1, by],   fill=IR_HL)

    # Moss patches (damp lower edges)
    for mx, my in MOSS_POS:
        d.ellipse([mx-5, my-2, mx+5, my+2], fill=MO_DK)
        d.ellipse([mx-3, my-1, mx+3, my+1], fill=MO_LT)

    return add_outline(img)


# ═══════════════════════════════════════════════════════════════════════════════
#  CEILING EDGE — bottom face of the ceiling with hanging stalactites
# ═══════════════════════════════════════════════════════════════════════════════

STONE_H = 18   # px of solid stone at the top of the cell

# Stalactites: (center_x, tip_y, base_half_width)
# Varied heights so they don't look uniform. None touch x=0 or x=47 → tiles cleanly.
STALACTITES = [
    ( 7, 40, 4),   # left   — long
    (19, 30, 3),   # center-left — short
    (32, 44, 5),   # center-right — longest, widest
    (44, 34, 3),   # right — medium
]

# Moss hanging from the stone bottom edge
EDGE_MOSS = [12, 26, 40]


def make_ceiling_edge():
    img = Image.new('RGBA', (CELL, CELL), T)
    d   = ImageDraw.Draw(img)
    px  = img.load()

    # ── Solid stone cap (top STONE_H rows) ───────────────────────────
    d.rectangle([0, 0, CELL-1, STONE_H-1], fill=ST_MD)

    # Facets in the stone cap
    d.polygon([(1, 1),(20, 0),(22, 8),(2, 9)],  fill=ST_LT)
    d.polygon([(24, 0),(46, 1),(46, 9),(26, 8)], fill=ST_LT)
    d.line([(1,1),(20,0)],   fill=ST_HL, width=1)
    d.line([(24,0),(46,1)],  fill=ST_HL, width=1)

    # Crack in the cap
    d.line([(22,0),(22,8),(20,14),(22,STONE_H)], fill=ST_CR, width=1)

    # Rough bottom edge of the stone cap
    rough = {4:2, 5:2, 14:1, 15:1, 28:2, 29:2, 42:1, 43:1}
    for x in range(CELL):
        extra = rough.get(x, 0)
        for dy in range(extra + 1):
            if STONE_H + dy < CELL:
                px[x, STONE_H + dy] = ST_DK

    # Moss hanging from bottom edge
    for mx in EDGE_MOSS:
        d.ellipse([mx-3, STONE_H-1, mx+3, STONE_H+3], fill=MO_DK)
        d.ellipse([mx-2, STONE_H,   mx+2, STONE_H+2], fill=MO_LT)

    # ── Stalactites ───────────────────────────────────────────────────
    for cx, tip_y, bhw in STALACTITES:
        height = tip_y - STONE_H

        for y in range(STONE_H, tip_y + 1):
            progress = (y - STONE_H) / height           # 0 at base, 1 at tip
            half_w   = max(0, bhw * (1.0 - progress))
            half_w_i = int(half_w + 0.5)

            for x in range(cx - half_w_i, cx + half_w_i + 1):
                if not (0 <= x < CELL and 0 <= y < CELL):
                    continue
                rel = x - cx
                # Shading: left highlight, center crack, right shadow
                if half_w_i == 0:
                    c = ST_LT
                elif rel == -half_w_i:
                    c = ST_LT           # left rim — light catch
                elif rel == half_w_i:
                    c = ST_DK           # right rim — shadow
                elif rel == 0 and progress > 0.2:
                    c = ST_CR           # centre crack
                else:
                    c = ST_MD
                px[x, y] = c

        # Water drop at tip (tiny blue bead)
        for wy in range(tip_y - 1, min(tip_y + 2, CELL)):
            if 0 <= cx < CELL and 0 <= wy < CELL:
                px[cx, wy] = WD
        if 0 <= cx < CELL and tip_y < CELL:
            px[cx, tip_y] = WD_HL      # brightest at the very tip

    return add_outline(img)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRANCE WALL — left-boundary dungeon wall, tiles vertically
# ═══════════════════════════════════════════════════════════════════════════════

# Horizontal mortar seams (block rows when stacked vertically)
WALL_MORTAR_Y = [16, 32]
# Vertical seam (one column joint inside the tile)
WALL_MORTAR_X = [24]
# Crack paths — more vertical character than ceiling cracks
WALL_CRACKS = [
    [(10, 0), (12, 10), ( 9, 20), (11, 32), ( 8, 48)],
    [(34, 0), (33, 16), (36, 28), (35, 48)],
]
# Stone facet quads — give sense of cut blocks
WALL_FACETS = [
    [( 1,  1), (22,  0), (23,  9), ( 2, 10)],
    [(26,  0), (46,  1), (47, 10), (27,  9)],
    [( 1, 18), (22, 17), (22, 30), ( 1, 31)],
    [(26, 18), (46, 17), (46, 30), (27, 30)],
    [( 1, 34), (22, 33), (22, 46), ( 1, 46)],
    [(26, 34), (46, 33), (46, 46), (27, 46)],
]
# Iron bolts
WALL_BOLTS = [(6, 8), (41, 8), (6, 40), (41, 40)]
# Moss clusters (right-edge damp corner)
WALL_MOSS = [(44, 16), (44, 32), (44, 46)]
# Right-edge face: bright rim, then a shadow band (depth effect)
EDGE_RIM_W  = 2   # px of ST_LT catch-light on the right edge
EDGE_SHAD_W = 5   # px of ST_DK shadow just inside the rim


def make_wall_tile():
    img = Image.new('RGBA', (CELL, CELL), T)
    d   = ImageDraw.Draw(img)
    px  = img.load()

    # Base stone fill
    d.rectangle([0, 0, CELL-1, CELL-1], fill=ST_MD)

    # Facets
    for pts in WALL_FACETS:
        d.polygon(pts, fill=ST_LT)
        d.line([pts[0], pts[1]], fill=ST_HL, width=1)

    # Mortar seams
    for y in WALL_MORTAR_Y:
        d.line([(0, y), (CELL-1, y)], fill=ST_DK, width=2)
    for x in WALL_MORTAR_X:
        for i, seg in enumerate([
            (0,                  WALL_MORTAR_Y[0] - 1),
            (WALL_MORTAR_Y[0]+2, WALL_MORTAR_Y[1] - 1),
            (WALL_MORTAR_Y[1]+2, CELL - 1),
        ]):
            d.line([(x + i*6, seg[0]), (x + i*6, seg[1])], fill=ST_DK, width=2)

    # Cracks
    for path in WALL_CRACKS:
        for i in range(len(path) - 1):
            d.line([path[i], path[i+1]], fill=ST_CR, width=1)

    # Iron bolts
    for bx, by in WALL_BOLTS:
        d.ellipse([bx-3, by-3, bx+3, by+3], fill=IR_MD)
        d.ellipse([bx-1, by-2, bx+1, by],   fill=IR_HL)

    # Moss on right edge
    for mx, my in WALL_MOSS:
        d.ellipse([mx-5, my-2, mx+5, my+2], fill=MO_DK)
        d.ellipse([mx-3, my-1, mx+3, my+1], fill=MO_LT)

    # Right-face bevel: shadow band then bright rim
    for x in range(CELL - EDGE_SHAD_W - EDGE_RIM_W, CELL - EDGE_RIM_W):
        for y in range(CELL):
            px[x, y] = ST_DK
    for x in range(CELL - EDGE_RIM_W, CELL):
        for y in range(CELL):
            px[x, y] = ST_LT

    return add_outline(img)


# ═══════════════════════════════════════════════════════════════════════════════
#  TORCH — wall-mounted bracket torch, flames upward, 48×48
# ═══════════════════════════════════════════════════════════════════════════════

def make_torch():
    img = Image.new('RGBA', (CELL, CELL), T)
    d   = ImageDraw.Draw(img)
    px  = img.load()

    cx = CELL // 2   # 24 — horizontal centre of the torch

    # ── Wall bracket (bottom, iron) ──────────────────────────────────────────
    # Horizontal bar
    d.rectangle([cx - 12, 38, cx + 12, 41], fill=IR_MD)
    d.line([(cx - 12, 38), (cx + 12, 38)], fill=IR_HL, width=1)
    # Vertical mount pin to wall (right side)
    d.rectangle([cx + 8, 38, cx + 12, CELL - 1], fill=IR_MD)
    d.line([(cx + 12, 38), (cx + 12, CELL - 1)], fill=IR_HL, width=1)
    # Rust accent
    d.point((cx + 10, 44), fill=IR_RST)
    d.point((cx + 10, 46), fill=IR_RST)

    # ── Torch body (wood handle) ─────────────────────────────────────────────
    # Main pole: 6px wide, from just above bracket up to flame base
    d.rectangle([cx - 3, 20, cx + 3, 38], fill=WD_BR)
    # Left shadow edge
    d.line([(cx - 3, 20), (cx - 3, 38)], fill=WD_DK, width=1)
    # Right highlight
    d.line([(cx + 3, 20), (cx + 3, 38)], fill=WD_BR, width=1)
    # Wood grain lines
    for gy in [24, 28, 32]:
        d.line([(cx - 2, gy), (cx + 2, gy)], fill=WD_DK, width=1)
    # Binding wrap (iron strip at top of handle)
    d.rectangle([cx - 4, 18, cx + 4, 21], fill=IR_MD)
    d.line([(cx - 4, 18), (cx + 4, 18)], fill=IR_HL, width=1)

    # ── Torch head / fuel cup (iron bowl) ───────────────────────────────────
    d.ellipse([cx - 6, 14, cx + 6, 20], fill=IR_DK)
    d.line([(cx - 6, 14), (cx + 6, 14)], fill=IR_LT, width=1)

    # ── Flame ────────────────────────────────────────────────────────────────
    # Outer dark base glow — widest
    for y in range(10, 16):
        prog = (y - 10) / 6.0
        hw = int(6 * (1.0 - prog) + 0.5)
        for x in range(cx - hw, cx + hw + 1):
            if 0 <= x < CELL:
                px[x, y] = FL_DK

    # Mid orange body
    for y in range(4, 12):
        prog = (y - 4) / 8.0
        hw = int(4 * (1.0 - prog * 0.7) + 0.5)
        for x in range(cx - hw, cx + hw + 1):
            if 0 <= x < CELL:
                px[x, y] = FL_MD

    # Hot yellow core
    for y in range(1, 9):
        prog = (y - 1) / 8.0
        hw = int(2 * (1.0 - prog) + 0.5)
        for x in range(cx - hw, cx + hw + 1):
            if 0 <= x < CELL:
                px[x, y] = FL_HT

    # Flicker wisp — single pixel tip
    if 0 <= cx < CELL:
        px[cx, 0] = FL_HT
        px[cx - 1, 2] = FL_MD   # slight lean left (draft)

    return add_outline(img)


# ═══════════════════════════════════════════════════════════════════════════════
#  ASSEMBLE AND SAVE
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating level assets...\n")
save_single(make_ceiling_tile(), '../assets/level/ceiling_tile.png')
print()
save_single(make_ceiling_edge(), '../assets/level/ceiling_edge.png')
print()
save_single(make_wall_tile(), '../assets/level/wall_tile.png')
print()
save_single(make_torch(), '../assets/level/torch.png')
print()
print("Done. Files written to assets/level/")
