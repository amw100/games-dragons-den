extends Node2D

## World layout — both values are in world-pixels.
## Default assumes 1152×648 viewport with no camera zoom.
const PLAY_TOP    := 0.0
const PLAY_BOTTOM := 576.0

## Sprite constants — must match make_sprites.py / make_obstacles.py
const TILE_W := 48
const TILE_H := 48
const GAP    := 2

## Tile pool — enough columns to fill the viewport plus a buffer on each side.
## Viewport = 1152px → 24 tiles visible; 30 gives 3 tiles of buffer per side.
const POOL_COLS := 30
const START_X   := -700.0   # x-centre of first pool column at startup

var _lava_frame := 0

# ── Ceiling pool (one edge sprite + one body sprite per column) ────────────────
var _ceil_edge  : Array[Sprite2D] = []
var _ceil_body  : Array[Sprite2D] = []
var _ceil_head  := 0       # pool index of the leftmost (oldest) column
var _ceil_right := 0.0     # x-centre of the rightmost placed column

# ── Floor pool (one lava_top + three lava_body sprites per column) ─────────────
var _floor_top  : Array[Sprite2D] = []
var _floor_body : Array[Sprite2D] = []   # 3 per column, index = col*3 + row
var _floor_head := 0
var _floor_right := 0.0


func _ready() -> void:
	_build_ceiling()
	_build_floor()
	_build_bounds_collision()

	var timer := Timer.new()
	timer.name       = "LavaTimer"
	timer.wait_time  = 1.0 / 8.0
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

		var top := Sprite2D.new()
		top.texture        = top_tex
		top.region_enabled = true
		top.region_rect    = _lava_region(0)
		top.position       = Vector2(x, PLAY_BOTTOM + TILE_H * 0.5)
		container.add_child(top)
		_floor_top.append(top)

		for row in 3:
			var b := Sprite2D.new()
			b.texture        = body_tex
			b.region_enabled = true
			b.region_rect    = _lava_region(0)
			b.position       = Vector2(x, PLAY_BOTTOM + TILE_H * (1.5 + row))
			container.add_child(b)
			_floor_body.append(b)

	_floor_right = START_X + (POOL_COLS - 1) * TILE_W


# ── Bounds collision — one wide slab each, never need to move ──────────────────

const KillZone := preload("res://scenes/kill_zone.tscn")

func _build_bounds_collision() -> void:
	var half_w := 100_000.0

	# Ceiling — static collision + kill zone
	var ceil_body := StaticBody2D.new()
	ceil_body.name = "CeilingCollision"
	add_child(ceil_body)
	var cc := CollisionShape2D.new()
	var cr := RectangleShape2D.new()
	cr.size     = Vector2(half_w * 2, TILE_H * 4)
	cc.shape    = cr
	cc.position = Vector2(0.0, PLAY_TOP - TILE_H * 2.0)
	ceil_body.add_child(cc)

	var ceil_kz   := KillZone.instantiate()
	var ceil_kz_c := CollisionShape2D.new()
	var ceil_kz_r := RectangleShape2D.new()
	ceil_kz_r.size     = Vector2(half_w * 2, TILE_H * 2)
	ceil_kz_c.shape    = ceil_kz_r
	ceil_kz_c.position = Vector2(0.0, PLAY_TOP)   # extends 48px into play area
	ceil_kz.add_child(ceil_kz_c)
	add_child(ceil_kz)

	# Floor — static collision + kill zone
	var floor_body := StaticBody2D.new()
	floor_body.name = "FloorCollision"
	add_child(floor_body)
	var fc := CollisionShape2D.new()
	var fr := RectangleShape2D.new()
	fr.size     = Vector2(half_w * 2, TILE_H * 5)
	fc.shape    = fr
	fc.position = Vector2(0.0, PLAY_BOTTOM + TILE_H * 2.5)
	floor_body.add_child(fc)

	var floor_kz   := KillZone.instantiate()
	var floor_kz_c := CollisionShape2D.new()
	var floor_kz_r := RectangleShape2D.new()
	floor_kz_r.size     = Vector2(half_w * 2, TILE_H * 2)
	floor_kz_c.shape    = floor_kz_r
	floor_kz_c.position = Vector2(0.0, PLAY_BOTTOM)   # extends 48px into play area
	floor_kz.add_child(floor_kz_c)
	add_child(floor_kz)


# ── Tile recycling ─────────────────────────────────────────────────────────────

func _process(_delta: float) -> void:
	var cam_right : float = $Player.position.x + 620.0   # half-viewport + 1 tile buffer
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
		_floor_top[_floor_head].position.x = new_x
		for row in 3:
			_floor_body[_floor_head * 3 + row].position.x = new_x
		_floor_head  = (_floor_head + 1) % POOL_COLS
		_floor_right = new_x


# ── Lava animation ─────────────────────────────────────────────────────────────

func _lava_region(frame: int) -> Rect2:
	return Rect2(GAP + frame * (TILE_W + GAP), GAP, TILE_W, TILE_H)

func _advance_lava() -> void:
	_lava_frame = (_lava_frame + 1) % 4
	var region := _lava_region(_lava_frame)
	for spr in _floor_top:
		spr.region_rect = region
	for spr in _floor_body:
		spr.region_rect = region
