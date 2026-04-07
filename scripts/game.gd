class_name Game
extends Node2D

## World layout — both values are in world-pixels.
## Default assumes 1152×648 viewport with no camera zoom.
const PLAY_TOP    := 0.0
const PLAY_BOTTOM := 576.0

## Sprite constants — must match make_sprites.py / make_obstacles.py
const TILE_W := 48
const TILE_H := 48
const GAP    := 2

## Viewport width (must match project.godot display settings). Used to
## derive both the tile pool size and the camera look-ahead distance so that
## changing the viewport only requires updating this one constant.
const VIEWPORT_W := 1152

## Tile pool: enough columns to fill the viewport plus 2 tiles of buffer on
## each side. Derived from VIEWPORT_W/TILE_W so it scales with the window.
const POOL_COLS := 28   # ceil(1152 / 48) + 4 = 28

## Look-ahead for tile recycling: half the viewport plus one tile of slack.
## A column that scrolls past this distance behind the player is recycled.
const CAM_LEAD := VIEWPORT_W * 0.5 + TILE_W   # = 624

## x-centre of the first pool column at startup. Chosen so the initial pool
## covers the visible area on both sides of the player's spawn position.
const START_X := -700.0

## Collision world extents — wide enough that the player never reaches either
## end during a single play session. No recycling needed.
const WORLD_HALF_WIDTH := 100_000.0

## Packed scenes
const KillZoneScene := preload("res://scenes/kill_zone.tscn")

## Pre-computed lava-strip source rects — one per animation frame.
## Both lava_top and lava_body share the same 4-col strip layout.
var _lava_regions : Array[Rect2] = [
	Rect2(GAP + 0 * (TILE_W + GAP), GAP, TILE_W, TILE_H),
	Rect2(GAP + 1 * (TILE_W + GAP), GAP, TILE_W, TILE_H),
	Rect2(GAP + 2 * (TILE_W + GAP), GAP, TILE_W, TILE_H),
	Rect2(GAP + 3 * (TILE_W + GAP), GAP, TILE_W, TILE_H),
]

var _lava_frame := 0

# ── Ceiling pool ──────────────────────────────────────────────────────────────
var _ceil_edge  : Array[Sprite2D] = []
var _ceil_body  : Array[Sprite2D] = []
var _ceil_head  := 0       # pool index of the leftmost (oldest) column
var _ceil_right := 0.0     # x-centre of the rightmost placed column

# ── Floor pool ────────────────────────────────────────────────────────────────
# Each inner Array holds the sprites that make up one column:
#   index 0   = lava_top
#   index 1-3 = three lava_body rows stacked below
var _floor_cols  : Array = []
var _floor_head  := 0
var _floor_right := 0.0

@onready var _player : CharacterBody2D = $Player


func _ready() -> void:
	_build_ceiling()
	_build_floor()
	_build_bounds_collision()

	var timer := Timer.new()
	timer.name       = "LavaTimer"
	timer.wait_time  = 1.0 / 8.0     # 8 FPS, matches make_obstacles.py design
	timer.autostart  = true
	timer.timeout.connect(_advance_lava)
	add_child(timer)


# ── Ceiling ────────────────────────────────────────────────────────────────────

func _build_ceiling() -> void:
	var container := Node2D.new()
	container.name = "CeilingSprites"
	add_child(container)

	var edge_tex : Texture2D = preload("res://assets/level/ceiling_edge.png")
	var tile_tex : Texture2D = preload("res://assets/level/ceiling_tile.png")
	var crop := Rect2(GAP, GAP, TILE_W, TILE_H)

	for i in POOL_COLS:
		var x := START_X + i * TILE_W

		var edge := Sprite2D.new()
		edge.texture        = edge_tex
		edge.region_enabled = true
		edge.region_rect    = crop
		edge.position       = Vector2(x, PLAY_TOP - TILE_H * 0.5)
		container.add_child(edge)
		_ceil_edge.append(edge)

		var tile := Sprite2D.new()
		tile.texture        = tile_tex
		tile.region_enabled = true
		tile.region_rect    = crop
		tile.position       = Vector2(x, PLAY_TOP - TILE_H * 1.5)
		container.add_child(tile)
		_ceil_body.append(tile)

	_ceil_right = START_X + (POOL_COLS - 1) * TILE_W


# ── Lava floor ─────────────────────────────────────────────────────────────────

func _build_floor() -> void:
	var container := Node2D.new()
	container.name = "FloorSprites"
	add_child(container)

	var top_tex  : Texture2D = preload("res://assets/obstacles/lava_top.png")
	var body_tex : Texture2D = preload("res://assets/obstacles/lava_body.png")

	for i in POOL_COLS:
		var x := START_X + i * TILE_W
		var col : Array[Sprite2D] = []

		var top := Sprite2D.new()
		top.texture        = top_tex
		top.region_enabled = true
		top.region_rect    = _lava_regions[0]
		top.position       = Vector2(x, PLAY_BOTTOM + TILE_H * 0.5)
		container.add_child(top)
		col.append(top)

		for row in 3:
			var b := Sprite2D.new()
			b.texture        = body_tex
			b.region_enabled = true
			b.region_rect    = _lava_regions[0]
			b.position       = Vector2(x, PLAY_BOTTOM + TILE_H * (1.5 + row))
			container.add_child(b)
			col.append(b)

		_floor_cols.append(col)

	_floor_right = START_X + (POOL_COLS - 1) * TILE_W


# ── Bounds collision + kill zones ──────────────────────────────────────────────

func _build_bounds_collision() -> void:
	# Ceiling: 4-tile-tall slab centred two tiles above PLAY_TOP so its bottom
	# edge lands on y = 0. Kill zone straddles PLAY_TOP so the player's circle
	# actually overlaps it when the static slab stops the body at the wall.
	_make_bounds_pair("Ceiling",
		PLAY_TOP - TILE_H * 2.0, TILE_H * 4,   # static slab: centre_y, height
		PLAY_TOP)                              # kill-zone centre (2-tile tall)

	# Floor: 5-tile-tall slab (lava top + 3 body rows + padding).
	_make_bounds_pair("Floor",
		PLAY_BOTTOM + TILE_H * 2.5, TILE_H * 5,
		PLAY_BOTTOM)


func _make_bounds_pair(name_prefix: String,
		slab_centre_y: float, slab_h: float,
		kz_centre_y: float) -> void:
	var world_w := WORLD_HALF_WIDTH * 2

	# Static collision slab — blocks the player at the boundary.
	var body := StaticBody2D.new()
	body.name = name_prefix + "Collision"
	var col  := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size    = Vector2(world_w, slab_h)
	col.shape    = rect
	col.position = Vector2(0.0, slab_centre_y)
	body.add_child(col)
	add_child(body)

	# Kill zone Area2D — straddles the boundary so the player's circle overlaps
	# it on contact. Height of TILE_H * 2 (96px) is comfortably larger than the
	# player radius (~25px) to guarantee overlap at the stop position.
	var kz : Area2D = KillZoneScene.instantiate()
	kz.name = name_prefix + "KillZone"
	var kz_col  := CollisionShape2D.new()
	var kz_rect := RectangleShape2D.new()
	kz_rect.size    = Vector2(world_w, TILE_H * 2)
	kz_col.shape    = kz_rect
	kz_col.position = Vector2(0.0, kz_centre_y)
	kz.add_child(kz_col)
	add_child(kz)


# ── Tile recycling ─────────────────────────────────────────────────────────────

func _process(_delta: float) -> void:
	var cam_right := _player.position.x + CAM_LEAD
	_scroll_ceil(cam_right)
	_scroll_floor(cam_right)


func _scroll_ceil(cam_right: float) -> void:
	while _ceil_right < cam_right + TILE_W:
		var new_x := _ceil_right + TILE_W
		_ceil_edge[_ceil_head].position.x = new_x
		_ceil_body[_ceil_head].position.x = new_x
		_ceil_head  = (_ceil_head + 1) % POOL_COLS
		_ceil_right = new_x


func _scroll_floor(cam_right: float) -> void:
	while _floor_right < cam_right + TILE_W:
		var new_x := _floor_right + TILE_W
		for spr in _floor_cols[_floor_head]:
			spr.position.x = new_x
		_floor_head  = (_floor_head + 1) % POOL_COLS
		_floor_right = new_x


# ── Lava animation ─────────────────────────────────────────────────────────────

func _advance_lava() -> void:
	_lava_frame = (_lava_frame + 1) % 4
	var region := _lava_regions[_lava_frame]
	for col in _floor_cols:
		for spr in col:
			spr.region_rect = region
