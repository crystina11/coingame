extends Node
## Global game state: coins, milestones, worlds, skins, save/load.

signal coins_changed(total: int)
signal milestone_reached(world_id: String)
signal skin_unlocked(skin_id: String)

const SAVE_PATH := "user://coin_collector_save.cfg"

const WORLDS := [
	{
		"id": "meadow", "name": "Sunny Meadow", "coins_needed": 0,
		"music": "res://assets/audio/music_theme.wav",
		"coin_tex": "res://assets/sprites/coins/gold_spin.png",
		"sky_top": Color("6aa8e0"), "sky_bot": Color("bfe3f5"),
		"tile_top": "res://assets/sprites/tiles/grass_top.png",
		"tile_fill": "res://assets/sprites/tiles/dirt.png",
		"deco": ["res://assets/sprites/deco/pine.png", "res://assets/sprites/deco/flower.png",
			"res://assets/sprites/deco/rock.png", "res://assets/sprites/deco/cloud.png"],
		"enemies": ["slime_green", "slime_green", "bat"],
	},
	{
		"id": "snow", "name": "Snow Town", "coins_needed": 100,
		"music": "res://assets/audio/music_snow.wav",
		"coin_tex": "res://assets/sprites/coins/snow_spin.png",
		"sky_top": Color("3d4a6b"), "sky_bot": Color("cfe4f7"),
		"tile_top": "res://assets/sprites/tiles/snow_top.png",
		"tile_fill": "res://assets/sprites/tiles/ice.png",
		"deco": ["res://assets/sprites/deco/pine_snow.png", "res://assets/sprites/deco/igloo.png",
			"res://assets/sprites/deco/rock_snow.png", "res://assets/sprites/deco/lamp.png"],
		"enemies": ["slime_ice", "slime_ice", "bat"],
	},
	{
		"id": "beach", "name": "Beach", "coins_needed": 300,
		"music": "res://assets/audio/music_beach.wav",
		"coin_tex": "res://assets/sprites/coins/shell_spin.png",
		"sky_top": Color("ffb75e"), "sky_bot": Color("ffe9b0"),
		"tile_top": "res://assets/sprites/tiles/sand_top.png",
		"tile_fill": "res://assets/sprites/tiles/sand.png",
		"deco": ["res://assets/sprites/deco/palm.png", "res://assets/sprites/deco/cactus.png",
			"res://assets/sprites/deco/shell.png", "res://assets/sprites/deco/hut.png"],
		"enemies": ["slime_sand", "slime_sand", "bat", "slime_king"],
	},
]

const SKIN_UNLOCKS := {
	25: "ninja",
	100: "yeti",
	200: "surfer",
	300: "robot",
	500: "explorer",
}

const ALL_SKINS := ["hero", "ninja", "yeti", "surfer", "robot", "explorer"]

var total_coins: int = 0      # lifetime coins (drives progression)
var run_coins: int = 0        # coins held this run (lost on death)
var best_run: int = 0
var deaths: int = 0
var unlocked_skins: Array[String] = ["hero"]
var current_skin: String = "hero"
var highest_world: int = 0
var current_world: int = 0


func _ready() -> void:
	load_game()
	milestone_check(true)


func add_coin(value: int = 1) -> void:
	total_coins += value
	run_coins += value
	if run_coins > best_run:
		best_run = run_coins
	GameStats.coins_picked_up += value
	coins_changed.emit(total_coins)
	milestone_check(false)


func milestone_check(silent: bool) -> void:
	for widx in range(1, WORLDS.size()):
		var need: int = WORLDS[widx]["coins_needed"]
		if total_coins >= need and highest_world < widx:
			highest_world = widx
			if not silent:
				milestone_reached.emit(WORLDS[widx]["id"])
	for m in SKIN_UNLOCKS.keys():
		if total_coins >= m:
			var sid: String = SKIN_UNLOCKS[m]
			if sid not in unlocked_skins:
				unlocked_skins.append(sid)
				if not silent:
					skin_unlocked.emit(sid)


func world_unlocked(widx: int) -> bool:
	return widx <= highest_world


func set_skin(sid: String) -> void:
	if sid in unlocked_skins:
		current_skin = sid
		save_game()


func lose_run_coins() -> void:
	run_coins = 0
	deaths += 1


func save_game() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("progress", "total_coins", total_coins)
	cfg.set_value("progress", "best_run", best_run)
	cfg.set_value("progress", "deaths", deaths)
	cfg.set_value("progress", "highest_world", highest_world)
	cfg.set_value("progress", "unlocked_skins", PackedStringArray(unlocked_skins))
	cfg.set_value("progress", "current_skin", current_skin)
	cfg.save(SAVE_PATH)


func load_game() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) != OK:
		return
	total_coins = cfg.get_value("progress", "total_coins", 0)
	best_run = cfg.get_value("progress", "best_run", 0)
	deaths = cfg.get_value("progress", "deaths", 0)
	highest_world = cfg.get_value("progress", "highest_world", 0)
	var arr: PackedStringArray = cfg.get_value("progress", "unlocked_skins", PackedStringArray(["hero"]))
	unlocked_skins.clear()
	for s in arr:
		unlocked_skins.append(s)
	if unlocked_skins.is_empty():
		unlocked_skins.append("hero")
	current_skin = cfg.get_value("progress", "current_skin", "hero")
	if current_skin not in unlocked_skins:
		current_skin = "hero"


func reset_save() -> void:
	DirAccess.remove_absolute(SAVE_PATH)
	total_coins = 0
	run_coins = 0
	best_run = 0
	deaths = 0
	highest_world = 0
	unlocked_skins = Array(["hero"])
	current_skin = "hero"

