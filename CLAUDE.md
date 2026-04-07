# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Dragon's Den — a Flappy Bird clone in Godot 4.6 (Forward Plus, D3D12 on Windows). The player controls a red pixel-art dragon flying through a dungeon. Bottom obstacles are animated lava columns; top obstacles are dungeon chains with iron spike balls.

Main scene is `scenes/game.tscn` (set in `project.godot`). Viewport is **1152×648** at 1× camera zoom.

## Scenes

- `scenes/game.tscn` — root `Node2D`, runs `scripts/game.gd`. Instances `player.tscn`; everything else (ceiling, floor, collision, kill zones) is built procedurally in the script. The player has a `Camera2D` child whose `limit_top = -36` and `limit_bottom = 612` lock the camera vertically at y=288 — these values assume the 1152×648 viewport; update them if the viewport changes.
- `scenes/player.tscn` — `CharacterBody2D` (in the `"player"` group) with two children:
  - `AnimatedSprite2D` — **two** animations in the `SpriteFrames` resource:
    - `"default"` (flying): Row 0 of `dragon.png`, 4 frames, 5 FPS, loop=false. Plays only while the dragon is actively flapping (spacebar); otherwise the sprite rests on frame 2.
    - `"death"`: Row 1 of `dragon.png`, 4 frames, 8 FPS, loop=false. Plays once when the player dies.
    - All frames are sliced with **50×51px `AtlasTexture` regions** (= CELL 48 + GAP 2) along the spritesheet.
  - `CollisionShape2D` — `CircleShape2D` radius ≈ 24.7px.
- `scenes/kill_zone.tscn` — reusable `Area2D` with `kill_zone.gd` attached. No `CollisionShape2D` baked in; the instancer adds the shape appropriate to its use. Currently used for the ceiling/floor kill zones (shapes added in `game.gd`) and will be reused for obstacles.

## Scripts

- `scripts/game.gd` (`class_name Game`) — attached to the `Game` node. At startup builds:
  1. A **recycling pool** of `POOL_COLS` ceiling columns (`_ceil_edge` + `_ceil_body`) and floor columns (`_floor_cols`, each inner array = 1 lava_top + 3 lava_body rows).
  2. Two single wide `StaticBody2D` collision slabs (`WORLD_HALF_WIDTH = 100_000`) — one each for ceiling and floor — via `_make_bounds_pair()`, which also creates a matching `KillZone` Area2D that straddles the boundary so the player's circle overlaps it on contact.
  3. A single 8 FPS `Timer` that drives lava animation by updating `region_rect` on every `_floor_cols` sprite from a pre-computed `_lava_regions` array.

  In `_process()`, `_scroll_ceil()` and `_scroll_floor()` reposition any column that has fallen behind the player by more than `CAM_LEAD` (half viewport + 1 tile) to `_*_right + TILE_W`, keeping the visuals infinite while memory stays bounded.

  Key constants — adjust these if the viewport or tile grid changes:
  - `PLAY_TOP = 0.0`, `PLAY_BOTTOM = 576.0`
  - `VIEWPORT_W = 1152`, `POOL_COLS = 28`, `CAM_LEAD = 624`
  - `TILE_W = TILE_H = 48`, `GAP = 2`

- `scripts/player.gd` (`class_name Player`) — horizontal `SPEED = 200`, flap impulse `FLAP_FORCE = -450`, death-to-restart delay `DEATH_TIME_SEC = 2.0`. Gravity and forward velocity run every physics frame; `ui_accept` (spacebar) flaps and plays the flying animation once. On contact with a kill zone, `die()` stops forward motion, plays the `"death"` animation, `await`s the death timer, then flips `_can_restart`. `_input()` then listens for any real key/button press (filtered by `is_pressed()` + `not is_echo()`) and reloads the scene.

- `scripts/kill_zone.gd` (`class_name KillZone`) — minimal `Area2D` script. On `body_entered`, if the body is in the `"player"` group it calls `body.die()`.

## Asset Pipeline

All sprites are generated programmatically via Python + Pillow. **Never hand-edit the PNG files directly** — regenerate them by running the scripts.

```bash
# Run from the tools/ directory
cd tools
python make_sprites.py    # regenerates assets/dragon/
python make_obstacles.py  # regenerates assets/obstacles/
python make_level.py      # regenerates assets/level/
```

Each script outputs:
- `*.png` — native resolution (what Godot imports)
- `*_4x.png` — 4× nearest-neighbor scaled preview for visual review only

## Asset Layout

- `assets/dragon/dragon.png` — 4-col × 2-row spritesheet, 48×48px per cell, 2px gap. When slicing in Godot use **50×51px AtlasTexture regions** (cell + gap) at y=0 for Row 0 and y=51 for Row 1.
  - Row 0 (y=0): flying animation (wings-up, mid-up, level, mid-down)
  - Row 1 (y=51): death animation (hit-flash, tilting, spinning, splat)
- `assets/obstacles/lava_top.png` — 4-frame strip, animated sine-wave lava surface
- `assets/obstacles/lava_body.png` — 4-frame strip, animated basalt body with upward-scrolling flow bands (synced frame index with lava_top)
- `assets/obstacles/chain_link.png` — single tileable iron chain link (poles at y=0–5 and y=42–47 for seamless vertical stacking)
- `assets/obstacles/chain_cap.png` — ceiling anchor bracket
- `assets/obstacles/spike_ball.png` — 64×64px spiked iron ball
- `assets/level/ceiling_tile.png` — tileable dungeon stone block, used above the ceiling edge
- `assets/level/ceiling_edge.png` — bottom face of ceiling with hanging stalactites
- `assets/level/wall_tile.png` — **generated but currently unused.** Vertical-tiling stone wall with a right-facing bevel; was made for an entrance prototype, kept on disk for future use. Do not delete without asking.
- `assets/level/torch.png` — **generated but currently unused.** Wall-mounted bracket torch with a layered flame; same story as `wall_tile.png`.

## Godot Import Settings (for all native PNGs)

Filter: **Nearest**, Mipmaps: **Off**, Compression: **Lossless**

## Key Design Decisions

**Lava animation sync:** `lava_top` and `lava_body` share the same 4-frame cycle at 8 FPS. `game.gd` drives all lava sprites from a single timer and a shared `_lava_frame` index so the sine-wave trough at the bottom of the top cap blends seamlessly into the body tiles below.

**Infinite ceiling/floor:** Implemented as a recycling tile pool (`POOL_COLS` columns) whose sprites teleport from the left edge to the right edge of the pool as the player advances. The physics collision is a single static slab per boundary (`WORLD_HALF_WIDTH` wide) and never moves — it's large enough that the player never reaches either end.

**Kill zone overlap trick:** The static collision slab stops the player exactly at the boundary (`y=0` for ceiling, `y=576` for floor). If the `Area2D` kill zone were flush with the slab, the player's circle would only touch the edge and `body_entered` would never fire. The kill-zone shapes are therefore centred **on** `PLAY_TOP` / `PLAY_BOTTOM` with a `TILE_H * 2` (96 px) height so they straddle the boundary and always overlap the player's circle on contact. This matters for future obstacles too.

**Camera:** `Camera2D` is a child of `Player` and follows horizontally. Vertical motion is locked by setting `limit_top = -36` / `limit_bottom = 612` — with a 648-px viewport, the legal camera-centre range collapses to a single point at y=288. If the viewport changes, recompute as `limit_top = -(viewport_h - 576)/2`, `limit_bottom = 576 + (viewport_h - 576)/2`.

**Sprite scale:** Everything is authored at 48×48px (64×64 for spike ball). Scale up uniformly in Godot — do not mix resolutions.

**Chain obstacle hitbox:** Use `CircleShape2D` with radius 14–18px on the spike ball only. The spikes are purely visual.

## tools/ Script Conventions

The three generators (`make_sprites.py`, `make_obstacles.py`, `make_level.py`) follow the same conventions:
- `CELL = 48`, `GAP = 2`, transparent background `RGBA (0,0,0,0)`
- `BK = (14, 5, 22, 255)` — shared outline color used on all assets
- `add_outline(img)` — 1px dark outline pass applied to every frame after drawing
- Paths are relative to `tools/` using `../assets/...`
- Save both native and 4× preview; print a summary line per file

Each script is intentionally self-contained (palettes + helpers duplicated across files) so they can be run independently without import ordering. Do not consolidate them into a shared module unless the duplication becomes painful.
