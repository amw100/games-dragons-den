# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Dragon's Den — a Flappy Bird clone in Godot 4.6 (Forward Plus, D3D12 on Windows). The player controls a red pixel-art dragon flying through a dungeon. Bottom obstacles are animated lava columns; top obstacles are dungeon chains with iron spike balls.

## Scenes

- `scenes/game.tscn` — root `Node2D`, runs `scripts/game.gd`. Spawns the ceiling and lava floor at runtime; instances `player.tscn`.
- `scenes/player.tscn` — `CharacterBody2D` with two children:
  - `AnimatedSprite2D` — plays the flying animation via a `SpriteFrames` resource (animation named `"default"`, 4 frames, 5 FPS, loop). Slices `dragon.png` using `AtlasTexture` regions of **50×51px** per frame (= CELL 48 + GAP 2) starting at x=0, 50, 100, 150 along Row 0.
  - `CollisionShape2D` — `CircleShape2D` radius ≈ 24.7px.

Main scene is `scenes/game.tscn` (set in `project.godot`).

## Scripts

- `scripts/game.gd` — attached to the `Game` node. Tiles `ceiling_edge` + `ceiling_tile` sprites across the top and `lava_top` + `lava_body` across the bottom at startup. Drives all lava animation from a single 8 FPS `Timer` (all tiles share frame index via `region_rect` updates). Key constants: `PLAY_TOP = 0.0`, `PLAY_BOTTOM = 576.0` — adjust if viewport size or camera zoom changes.

## Asset Pipeline

All sprites are generated programmatically via Python + Pillow. **Never hand-edit the PNG files directly** — regenerate them by running the scripts.

```bash
# Run from the tools/ directory
cd tools
python make_sprites.py    # regenerates assets/dragon/
python make_obstacles.py  # regenerates assets/obstacles/
```

Each script outputs:
- `*.png` — native resolution (what Godot imports)
- `*_4x.png` — 4× nearest-neighbor scaled preview for visual review only

## Asset Layout

- `assets/dragon/dragon.png` — 4-col × 2-row spritesheet, 48×48px per cell, 2px gap. When slicing in Godot use **50×51px AtlasTexture regions** (cell + gap) at y=0 for Row 0 and y=51 for Row 1.
  - Row 0 (y=0): flying animation (wings-up, mid-up, level, mid-down) — used by player
  - Row 1 (y=51): death animation (hit-flash, tilting, spinning, splat)
- `assets/obstacles/lava_top.png` — 4-frame strip, animated sine-wave lava surface
- `assets/obstacles/lava_body.png` — 4-frame strip, animated basalt body with upward-scrolling flow bands (synced frame index with lava_top)
- `assets/obstacles/chain_link.png` — single tileable iron chain link (poles at y=0–5 and y=42–47 for seamless vertical stacking)
- `assets/obstacles/chain_cap.png` — ceiling anchor bracket
- `assets/obstacles/spike_ball.png` — 64×64px spiked iron ball

## Godot Import Settings (for all native PNGs)

Filter: **Nearest**, Mipmaps: **Off**, Compression: **Lossless**

## Key Design Decisions

**Lava animation sync:** `lava_top` and `lava_body` share the same 4-frame cycle at 8 FPS. In Godot, drive all lava `AnimatedSprite2D` nodes from a single frame counter so the sine-wave trough at the bottom of the top cap blends seamlessly into the body tiles below.

**Sprite scale:** Everything is authored at 48×48px (64×64 for spike ball). Scale up uniformly in Godot — do not mix resolutions.

**Chain obstacle hitbox:** Use `CircleShape2D` with radius 14–18px on the spike ball only. The spikes are purely visual.

## tools/ Script Conventions

Both scripts follow the same conventions:
- `CELL = 48`, `GAP = 2`, transparent background `RGBA (0,0,0,0)`
- `BK = (14, 5, 22, 255)` — shared outline color used on all assets
- `add_outline(img)` — 1px dark outline pass applied to every frame after drawing
- Paths are relative to `tools/` using `../assets/...`
- Save both native and 4× preview; print a summary line per file
