"""
Dragon's Den — Obstacle asset generator
Produces 5 assets (10 PNGs: native 1× + 4× preview each):

  Lava column (bottom obstacle):
    assets/obstacles/lava_top.png   — 4-frame animated sine-wave lava surface
    assets/obstacles/lava_body.png  — 4-frame animated basalt body w/ upward flow bands

  Chain obstacle (top obstacle):
    assets/obstacles/chain_link.png — single tileable iron chain link
    assets/obstacles/chain_cap.png  — ceiling anchor bracket
    assets/obstacles/spike_ball.png — 64×64 spiked iron ball

Convention matches make_sprites.py exactly.
"""

import math
from PIL import Image, ImageDraw

# ── Grid constants (match make_sprites.py) ────────────────────────────────────
CELL    = 48
GAP     = 2
T       = (0, 0, 0, 0)
BK      = (14, 5, 22, 255)

# Spike ball uses a larger cell
CELL_LG = 64

# ── Lava palette ──────────────────────────────────────────────────────────────
LV_DK  = ( 90,  20,   4, 255)   # dark magma
LV_MD  = (192,  52,   8, 255)   # main lava orange
LV_LT  = (240, 112,  16, 255)   # bright highlight
LV_GLW = (252, 196,  48, 255)   # hot-core glow
LV_CRU = ( 52,  28,  12, 255)   # cooled crust skin

# ── Basalt palette ────────────────────────────────────────────────────────────
BS_DK      = ( 18,  16,  20, 255)   # deep basalt
BS_MD      = ( 42,  38,  46, 255)   # mid basalt
BS_LT      = ( 68,  62,  74, 255)   # face stone
BS_HLT     = ( 90,  84,  96, 255)   # chip highlight
LV_CRK     = (160,  40,   8, 255)   # lava crack glow
LV_CRK_LT  = (220, 100,  20, 255)   # crack bright core

# ── Iron palette ──────────────────────────────────────────────────────────────
IR_DK  = ( 28,  26,  30, 255)   # deep shadow
IR_MD  = ( 58,  54,  62, 255)   # main iron
IR_LT  = ( 96,  90, 102, 255)   # iron face
IR_HLT = (148, 144, 152, 255)   # sheen
IR_RIM = (180, 174, 186, 255)   # brightest catch-light
IR_RST = ( 72,  38,  18, 255)   # rust accent


# ── Utility ───────────────────────────────────────────────────────────────────

def add_outline(img, size=CELL):
    """1-px dark outline around all non-transparent, non-outline pixels."""
    src = img.load()
    out = img.copy()
    dst = out.load()
    bk3 = BK[:3]
    for y in range(size):
        for x in range(size):
            if src[x, y][3] == 0:
                for dy, dx in [(-1,0),(1,0),(0,-1),(0,1),
                                (-1,-1),(-1,1),(1,-1),(1,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < size and 0 <= ny < size:
                        nb = src[nx, ny]
                        if nb[3] > 0 and nb[:3] != bk3:
                            dst[x, y] = BK
                            break
    return out


def lerp_color(a, b, t):
    """Linear interpolate between two RGBA tuples."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


def save_strip(frames, path_1x, label):
    """Save a list of CELL×CELL Images as a horizontal strip + 4× preview."""
    n = len(frames)
    W = n * CELL + (n + 1) * GAP
    H = CELL + 2 * GAP
    sheet = Image.new('RGBA', (W, H), T)
    for i, fr in enumerate(frames):
        ox = GAP + i * (CELL + GAP)
        sheet.paste(fr, (ox, GAP), fr)
    sheet.save(path_1x)
    preview_path = path_1x.replace('.png', '_4x.png')
    sheet.resize((W * 4, H * 4), Image.NEAREST).save(preview_path)
    print(f"Saved {path_1x}  ({W}×{H}px)")
    print(f"Saved {preview_path}  ({W*4}×{H*4}px preview)")


def save_single(img, path_1x, cell=CELL):
    """Save a single-cell asset + 4× preview."""
    sz = cell + 2 * GAP
    sheet = Image.new('RGBA', (sz, sz), T)
    sheet.paste(img, (GAP, GAP), img)
    sheet.save(path_1x)
    preview_path = path_1x.replace('.png', '_4x.png')
    sheet.resize((sz * 4, sz * 4), Image.NEAREST).save(preview_path)
    print(f"Saved {path_1x}  ({sz}×{sz}px)")
    print(f"Saved {preview_path}  ({sz*4}×{sz*4}px preview)")


# ═══════════════════════════════════════════════════════════════════════════════
#  LAVA TOP — 4-frame sine-wave surface
# ═══════════════════════════════════════════════════════════════════════════════

# Hardcoded crust pixel positions (x, frame) where wave is near trough
CRUST_POSITIONS = {
    0: [6, 18, 30, 42, 10],
    1: [0, 24, 36, 14, 44],
    2: [12, 0, 42, 26, 6],
    3: [24, 6, 18, 38, 2],
}

def make_lava_top_frame(frame_idx):
    """
    Sine-wave lava surface scrolling +12px per frame.
    Wave period=48px, amplitude=7px, baseline y=18.
    """
    img   = Image.new('RGBA', (CELL, CELL), T)
    px    = img.load()
    offset = frame_idx * 12          # crest shifts right 12px per frame

    for x in range(CELL):
        wave_y = int(18 - 7 * math.sin(2 * math.pi * (x - offset) / 48))
        wave_y = max(4, min(26, wave_y))   # clamp so crest stays in cell

        for y in range(wave_y, CELL):
            depth = y - wave_y
            if depth <= 1:
                c = LV_GLW              # hot bright crest
            elif depth <= 5:
                c = LV_LT              # subsurface glow
            elif depth <= 10:
                c = LV_MD              # main lava body
            elif y >= CELL - 8:
                # bottom 8px: fade toward LV_DK to blend with body tile below
                t = (y - (CELL - 8)) / 8.0
                c = lerp_color(LV_MD, LV_DK, t)
            else:
                c = LV_MD
            px[x, y] = c

    # Scatter cooled crust pixels at trough positions
    for cx in CRUST_POSITIONS[frame_idx]:
        if cx < CELL:
            wave_y = int(18 - 7 * math.sin(2 * math.pi * (cx - offset) / 48))
            wave_y = max(4, min(26, wave_y))
            # Only paint crust at troughs (wave_y near baseline)
            if wave_y >= 17:
                px[cx, wave_y] = LV_CRU
                if cx + 1 < CELL:
                    px[cx + 1, wave_y] = LV_CRU

    return add_outline(img)


# ═══════════════════════════════════════════════════════════════════════════════
#  LAVA BODY — 4-frame upward-flowing bands + static crack overlay
# ═══════════════════════════════════════════════════════════════════════════════

# Static stone facets (same on all frames): list of polygon point lists
FACETS = [
    [(4,6),(14,4),(18,12),(8,16)],
    [(20,22),(32,18),(36,28),(24,32)],
    [(6,34),(16,30),(20,40),(10,44)],
    [(28,8),(40,6),(44,18),(34,20)],
    [(2,46),(12,42),(14,48),(2,48)],
]

# Crack flare nodes: (x, y) positions per crack line
CRACK_FLARES = {
    14: [8, 22, 38],
    26: [4, 16, 34, 46],
    38: [10, 28, 42],
}

def make_lava_body_frame(frame_idx):
    """
    Basalt body tile with scrolling lava-flow bands (4px upward shift/frame)
    and a static crack + stone-facet overlay.
    Band period=16px, 3 bands per 48px tile.
    """
    img = Image.new('RGBA', (CELL, CELL), T)
    px  = img.load()
    d   = ImageDraw.Draw(img)

    # ── Flow band layer ───────────────────────────────────────────────
    band_offset = frame_idx * 4      # shifts 4px up per frame
    period      = 16

    for y in range(CELL):
        # distance to nearest band center (with wrap)
        shifted_y = (y + band_offset) % period
        dist = min(shifted_y, period - shifted_y)
        if dist <= 2:
            c = LV_LT
        elif dist <= 4:
            c = LV_MD
        elif dist <= 7:
            t = (dist - 4) / 3.0
            c = lerp_color(LV_MD, BS_DK, t)
        else:
            c = BS_DK
        for x in range(CELL):
            px[x, y] = c

    # ── Stone facets ──────────────────────────────────────────────────
    for pts in FACETS:
        d.polygon(pts, fill=BS_MD)
        # highlight upper-left edge of each facet
        if len(pts) >= 2:
            d.line([pts[0], pts[1]], fill=BS_LT, width=1)
    # Chip highlights
    for cx, cy in [(8,8),(30,14),(18,36),(40,24),(12,46)]:
        if 0 <= cx < CELL and 0 <= cy < CELL:
            px[cx, cy] = BS_HLT

    # ── Lava crack lines (same on all frames for seamless stacking) ───
    for crack_x, flares in CRACK_FLARES.items():
        width = 2 if crack_x == 26 else 1
        for y in range(CELL):
            for dx in range(width):
                if crack_x + dx < CELL:
                    px[crack_x + dx, y] = LV_CRK
        # Flare nodes: 3px horizontal bright dash
        for fy in flares:
            if 0 <= fy < CELL:
                for dx in range(-1, 3):
                    nx = crack_x + dx
                    if 0 <= nx < CELL:
                        px[nx, fy] = LV_CRK_LT

    return add_outline(img)


# ═══════════════════════════════════════════════════════════════════════════════
#  CHAIN LINK — single tileable 48×48
# ═══════════════════════════════════════════════════════════════════════════════

def make_chain_link():
    """
    Iron oval ring (36×44) centered in 48×48.
    Poles at top (y=0–5) and bottom (y=42–47) so stacked tiles interlock.
    """
    img = Image.new('RGBA', (CELL, CELL), T)
    d   = ImageDraw.Draw(img)
    cx, cy = 24, 24

    # Connecting poles (top & bottom) — 10px wide
    d.rectangle([cx-5, 0, cx+5, 5],  fill=IR_MD)
    d.rectangle([cx-5, 42, cx+5, 47], fill=IR_MD)

    # Outer oval (ring base)
    d.ellipse([cx-18, cy-22, cx+18, cy+22], fill=IR_MD)

    # Inner cutout (hole)
    d.ellipse([cx-10, cy-14, cx+10, cy+14], fill=T)

    # Left arc shadow
    d.arc([cx-18, cy-22, cx+18, cy+22], start=120, end=240, fill=IR_DK, width=4)

    # Right arc highlight
    d.arc([cx-18, cy-22, cx+18, cy+22], start=300, end=60, fill=IR_LT, width=3)

    # Top-right catch-light
    d.arc([cx-18, cy-22, cx+18, cy+22], start=330, end=30, fill=IR_RIM, width=2)

    # Rust at bottom-left inner corner
    px = img.load()
    for (rx, ry) in [(cx-8, cy+12), (cx-9, cy+11), (cx-7, cy+13)]:
        if 0 <= rx < CELL and 0 <= ry < CELL and img.getpixel((rx, ry))[3] > 0:
            px[rx, ry] = IR_RST

    return add_outline(img)


# ═══════════════════════════════════════════════════════════════════════════════
#  CHAIN CAP — ceiling anchor bracket, single 48×48
# ═══════════════════════════════════════════════════════════════════════════════

def make_chain_cap():
    """
    U-bracket ceiling anchor.
    Top 28px: U-shape with mounting bolts.
    Bottom 20px: iron bar where chain attaches.
    """
    img = Image.new('RGBA', (CELL, CELL), T)
    d   = ImageDraw.Draw(img)

    # ── Top bar of U-bracket (full width) ────────────────────────────
    d.rectangle([0, 0, CELL-1, 8], fill=IR_MD)
    d.rectangle([0, 0, CELL-1, 8], outline=None)
    # highlight top face
    d.line([0,0, CELL-1,0], fill=IR_RIM, width=1)
    d.line([0,1, CELL-1,1], fill=IR_HLT, width=1)

    # ── Left upright ──────────────────────────────────────────────────
    d.rectangle([6, 8, 14, 28], fill=IR_MD)
    d.line([14, 8, 14, 28], fill=IR_LT, width=1)   # right face highlight
    d.line([ 6, 8,  6, 28], fill=IR_DK, width=1)   # left face shadow

    # ── Right upright ─────────────────────────────────────────────────
    d.rectangle([33, 8, 41, 28], fill=IR_MD)
    d.line([41, 8, 41, 28], fill=IR_LT, width=1)
    d.line([33, 8, 33, 28], fill=IR_DK, width=1)

    # ── Mounting bolts ────────────────────────────────────────────────
    for bx in [10, 37]:
        d.ellipse([bx-3, 2, bx+3, 8], fill=IR_LT)
        d.ellipse([bx-1, 3, bx+1, 6], fill=IR_RIM)

    # ── Rust patches at upright-to-bar junctions ─────────────────────
    for rx, ry in [(6,8),(13,8),(33,8),(40,8)]:
        d.rectangle([rx, ry, rx+2, ry+3], fill=IR_RST)

    # ── Bottom attachment bar (chain connects here) ───────────────────
    d.rectangle([6, 28, 41, 47], fill=IR_DK)    # shadow
    d.rectangle([7, 28, 41, 46], fill=IR_MD)    # face
    d.rectangle([7, 28, 41, 30], fill=IR_LT)    # top highlight
    d.rectangle([7, 43, 41, 46], fill=IR_DK)    # bottom shadow
    # Center groove (slot where chain ring passes)
    d.rectangle([20, 30, 27, 46], fill=IR_DK)

    return add_outline(img)


# ═══════════════════════════════════════════════════════════════════════════════
#  SPIKE BALL — single 64×64
# ═══════════════════════════════════════════════════════════════════════════════

SPIKE_DEFS = [
    # (angle_deg, tip_x, tip_y, base_left, base_right)
    (  0, 62, 32, (50, 29), (50, 35)),
    ( 45, 55, 55, (48, 43), (43, 49)),
    ( 90, 32, 62, (29, 50), (35, 50)),
    (135,  9, 55, (16, 43), (21, 49)),
    (180,  2, 32, (14, 35), (14, 29)),
    (225,  9,  9, (21, 15), (16, 21)),
    (270, 32,  2, (35, 14), (29, 14)),
    (315, 55,  9, (43, 15), (48, 21)),
]

def make_spike_ball():
    img = Image.new('RGBA', (CELL_LG, CELL_LG), T)
    d   = ImageDraw.Draw(img)
    cx, cy, r = 32, 32, 18

    # ── Spikes (drawn first, behind ball) ────────────────────────────
    for angle, tx, ty, bl, br in SPIKE_DEFS:
        # Fill triangle
        d.polygon([(tx, ty), bl, br], fill=IR_MD)
        # Left face highlight
        d.line([bl[0], bl[1], tx, ty], fill=IR_LT, width=1)
        # Right face shadow
        d.line([br[0], br[1], tx, ty], fill=IR_DK, width=1)
        # Tip catch-light
        if 0 <= tx < CELL_LG and 0 <= ty < CELL_LG:
            img.putpixel((tx, ty), IR_RIM)

    # ── Ball body ─────────────────────────────────────────────────────
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=IR_MD)    # main sphere

    # Shadow — lower-left quadrant
    d.ellipse([cx-r, cy-2, cx+2, cy+r], fill=IR_DK)

    # Highlight — upper-right
    d.ellipse([cx-2, cy-r, cx+r, cy+2], fill=IR_LT)

    # Bright catch-light
    d.ellipse([cx+6, cy-10, cx+10, cy-6], fill=IR_RIM)

    # Rust spots (hardcoded positions)
    px = img.load()
    for (rx, ry) in [(cx-8, cy+8), (cx-10, cy+4), (cx-6, cy+12),
                     (cx-12, cy+8), (cx-4, cy+10)]:
        if 0 <= rx < CELL_LG and 0 <= ry < CELL_LG:
            if img.getpixel((rx, ry))[3] > 0:
                px[rx, ry] = IR_RST

    return add_outline(img, size=CELL_LG)


# ═══════════════════════════════════════════════════════════════════════════════
#  ASSEMBLE AND SAVE
# ═══════════════════════════════════════════════════════════════════════════════

print("Generating obstacle assets...\n")

# Lava top (4-frame strip)
lava_top_frames = [make_lava_top_frame(i) for i in range(4)]
save_strip(lava_top_frames, '../assets/obstacles/lava_top.png', 'lava_top')
print()

# Lava body (4-frame strip)
lava_body_frames = [make_lava_body_frame(i) for i in range(4)]
save_strip(lava_body_frames, '../assets/obstacles/lava_body.png', 'lava_body')
print()

# Chain link (single)
save_single(make_chain_link(), '../assets/obstacles/chain_link.png')
print()

# Chain cap (single)
save_single(make_chain_cap(), '../assets/obstacles/chain_cap.png')
print()

# Spike ball (single, 64px cell)
save_single(make_spike_ball(), '../assets/obstacles/spike_ball.png', cell=CELL_LG)
print()

print("Done. Files written to assets/dragon/ and assets/obstacles/")
print()
print("Stacking check: lava_top frame 0 bottom edge (LV_DK) should")
print("blend smoothly into lava_body frame 0 top band.")
