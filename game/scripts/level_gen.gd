extends Node2D
## Procedurally generates a side-scrolling level for the current world.

const TILE := 16
const LEVEL_COLS := 240
const GROUND_ROW := 18
const ROWS := 24

var rng := RandomNumberGenerator.new()
var world_idx: int = 0
var world_def: Dictionary = {}
var heights: Array[int] = []

@onready var terrain: TileMapLayer = $Terrain
@onready var deco_layer: Node2D = $Deco
@onready var coin_layer: Node2D = $Coins
@onready var enemy_layer: Node2D = $Enemies
@onready var player_spawn: Marker2D = $PlayerSpawn


func _enter_tree() -> void:
	## Swap places with parent ("World") so the generator node itself becomes
	## the World container and $Terrain/$Deco/$Coins/$Enemies resolve correctly.
	var parent := get_parent()          # old World
	var grand := parent.get_parent()    # Level
	var my_idx := parent.get_index()
	var kids := get_children()
	for c in kids:
		remove_child(c)
	parent.remove_child(self)
	grand.remove_child(parent)
	for c in kids:
		parent.add_child(c)
	grand.add_child(parent)
	parent.name = "WorldOld"
	add_child(parent)
	grand.move_child(self, my_idx)
	name = "World"


func _ready() -> void:
	world_idx = Game.current_world
	world_def = Game.WORLDS[world_idx]
	rng.seed = 1337 + world_idx * 7919
	_build_tileset()
	_generate()


func _build_tileset() -> void:
	# Visual tiles only; collision is built as StaticBody2D runs in
	# _rebuild_collision() so no .tres resources are needed.
	var ts := TileSet.new()
	ts.tile_size = Vector2i(TILE, TILE)
	var src := TileSetAtlasSource.new()
	var top_tex: Texture2D = load(world_def["tile_top"])
	var fill_tex: Texture2D = load(world_def["tile_fill"])
	var img := Image.create(TILE * 2, TILE, false, Image.FORMAT_RGBA8)
	_blit(img, top_tex, Vector2i(0, 0))
	_blit(img, fill_tex, Vector2i(TILE, 0))
	src.texture = ImageTexture.create_from_image(img)
	src.texture_region_size = Vector2i(TILE, TILE)
	src.create_tile(Vector2i(0, 0))
	src.create_tile(Vector2i(1, 0))
	ts.add_source(src, 0)
	terrain.tile_set = ts


func _blit(dst: Image, src_tex: Texture2D, at: Vector2i) -> void:
	var src := src_tex.get_image()
	if src.get_format() != dst.get_format():
		src = src.duplicate()
		src.convert(dst.get_format())
	dst.blit_rect(src, Rect2i(0, 0, mini(src.get_width(), TILE), mini(src.get_height(), TILE)), at)


func _generate() -> void:
	# ---- heightmap
	var cur := GROUND_ROW
	for x in range(LEVEL_COLS):
		if x % rng.randi_range(6, 14) == 0:
			cur = clampi(cur + rng.randi_range(-2, 2), GROUND_ROW - 5, GROUND_ROW + 2)
		heights.append(cur)
	for x in range(0, 12):
		heights[x] = GROUND_ROW
	# ---- pits
	var pits: Array = []
	var px := 26
	while px < LEVEL_COLS - 14:
		if rng.randf() < 0.55:
			var pw := rng.randi_range(2, 3 + world_idx)
			for i in range(pw):
				heights[px + i] = ROWS + 5
			pits.append([px, pw])
			px += pw + rng.randi_range(9, 18)
		else:
			px += rng.randi_range(10, 20)
	# ---- paint terrain (manual collision shapes so no .tres needed)
	for x in range(LEVEL_COLS):
		if heights[x] > ROWS:
			continue
		for y in range(heights[x], ROWS):
			var coord := Vector2i(0, 0) if y == heights[x] else Vector2i(1, 0)
			terrain.set_cell(Vector2i(x, y), 0, coord)
	_rebuild_collision()
	# ---- bridge platforms over some pits
	for pit in pits:
		if rng.randf() < 0.55:
			var left := maxi(pit[0] - 1, 0)
			var py := clampi(heights[left], 4, ROWS) - rng.randi_range(2, 3)
			for i in range(pit[1] + 2):
				terrain.set_cell(Vector2i(left + i, py), 0, Vector2i(0, 0))
	# ---- floating platforms with coin arcs
	for _i in range(26 + world_idx * 6):
		var pxx := rng.randi_range(14, LEVEL_COLS - 7)
		var base := heights[pxx]
		if base > ROWS:
			continue
		var pyy := base - rng.randi_range(3, 6)
		var pw := rng.randi_range(2, 5)
		for i in range(pw):
			terrain.set_cell(Vector2i(pxx + i, pyy), 0, Vector2i(0, 0))
		for i in range(pw):
			if rng.randf() < 0.55:
				_add_coin((pxx + i) * TILE + 8.0, (pyy - 1) * TILE + 8.0)
	_rebuild_collision()
	# ---- ground coin trails
	var cx := 12
	while cx < LEVEL_COLS - 4:
		var run := rng.randi_range(3, 7)
		for i in range(run):
			var col: int = mini(cx + i, LEVEL_COLS - 1)
			var yy := heights[col]
			if yy <= ROWS and rng.randf() < 0.85:
				_add_coin(col * TILE + 8.0, (yy - 2) * TILE + 8.0)
		cx += run + rng.randi_range(4, 12)
	# ---- gems
	for g in range(3):
		var gx := rng.randi_range(40, LEVEL_COLS - 20)
		var gy := heights[gx]
		if gy <= ROWS:
			_add_gem(gx * TILE + 8.0, (gy - 4) * TILE + 8.0)
	# ---- decorations
	for x in range(2, LEVEL_COLS - 2):
		if heights[x] <= ROWS and rng.randf() < 0.10:
			_add_deco(x * TILE, heights[x] * TILE)
	# ---- enemies
	var spacing := 26 - world_idx * 4
	var ex := 32
	while ex < LEVEL_COLS - 8:
		if heights[ex] <= ROWS:
			var pool: Array = world_def["enemies"]
			var etype: String = pool[rng.randi_range(0, pool.size() - 1)]
			var ey := heights[ex] * TILE - 8.0
			if etype == "bat":
				ey = (heights[ex] - rng.randi_range(4, 6)) * TILE
			_add_enemy(etype, ex * TILE + 8.0, ey)
		ex += rng.randi_range(int(spacing / 2.0), spacing)
	player_spawn.position = Vector2(6 * TILE + 8.0, (heights[6] - 2) * TILE)


func _rebuild_collision() -> void:
	## One rectangle StaticBody2D per contiguous horizontal run of tiles at each row.
	for c in get_children():
		if c is StaticBody2D:
			c.queue_free()
	var solid := {}
	for cell in terrain.get_used_cells():
		solid[cell] = true
	# merge vertical runs too: build a set, then greedily create rects
	var cells := solid.keys()
	var used := {}
	for cell in cells:
		used[cell] = false
	for y in range(-4, ROWS + 3):
		var x := 0
		while x < LEVEL_COLS:
			if used.has(Vector2i(x, y)) and not used[Vector2i(x, y)]:
				var start := x
				while x < LEVEL_COLS and used.has(Vector2i(x, y)) and not used[Vector2i(x, y)]:
					used[Vector2i(x, y)] = true
					x += 1
				# extend downward while the same-width run exists
				var hgt := 1
				while true:
					var ok := true
					for xx in range(start, x):
						var key := Vector2i(xx, y + hgt)
						if not (used.has(key) and not used[key]):
							ok = false
							break
					if not ok:
						break
					for xx in range(start, x):
						used[Vector2i(xx, y + hgt)] = true
					hgt += 1
				_add_ground_body(start, y, x - start, hgt)
			else:
				x += 1


func _add_ground_body(start_x: int, row: int, width: int, height: int = 1) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	var col := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(width * TILE, height * TILE)
	col.shape = rect
	col.position = Vector2(start_x * TILE + width * TILE / 2.0, row * TILE + height * TILE / 2.0)
	body.add_child(col)
	add_child(body)


func _add_coin(wx: float, wy: float) -> void:
	var c := preload("res://scenes/world_coin.tscn").instantiate()
	c.position = Vector2(wx, wy)
	coin_layer.add_child(c)


func _add_gem(wx: float, wy: float) -> void:
	var c := preload("res://scenes/world_coin.tscn").instantiate()
	c.value = 10
	c.custom_tex = "res://assets/sprites/coins/gem.png"
	c.position = Vector2(wx, wy)
	coin_layer.add_child(c)


func _add_deco(wx: float, ground_y: float) -> void:
	var list: Array = world_def["deco"]
	var path: String = list[rng.randi_range(0, list.size() - 1)]
	var tex: Texture2D = load(path)
	var s := Sprite2D.new()
	s.texture = tex
	s.centered = true
	s.z_index = -5
	var hgt := tex.get_height()
	if path.ends_with("cloud.png"):
		s.position = Vector2(wx + 8.0, rng.randi_range(1, 5) * TILE)
	else:
		s.position = Vector2(wx + 8.0, ground_y - hgt / 2.0 + 1.0)
	deco_layer.add_child(s)


func _add_enemy(etype: String, wx: float, wy: float) -> void:
	var e := preload("res://scenes/enemy.tscn").instantiate()
	e.enemy_type = etype
	e.position = Vector2(wx, wy)
	enemy_layer.add_child(e)

