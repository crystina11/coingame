extends Node2D
## Level root: wires player <-> HUD <-> game state, world transitions, restart.

@onready var player: CharacterBody2D = $Player
@onready var hud: CanvasLayer = $HUD


func _ready() -> void:
	Audio.play_music(Game.WORLDS[Game.current_world]["music"])
	player.died.connect(_on_player_died)
	Game.coins_changed.connect(_on_coins_changed)
	Game.milestone_reached.connect(_on_milestone)
	Game.skin_unlocked.connect(_on_skin_unlocked)
	hud.setup(player)
	_on_coins_changed(Game.total_coins)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("restart"):
		get_tree().reload_current_scene()
	elif event.is_action_pressed("ui_cancel"):
		Game.save_game()
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_coins_changed(total: int) -> void:
	hud.update_coins(total, Game.run_coins)
	var next_w: int = Game.current_world + 1
	if next_w < Game.WORLDS.size():
		hud.set_goal("NEXT WORLD: %s @ %d" % [Game.WORLDS[next_w]["name"],
			Game.WORLDS[next_w]["coins_needed"]])
	else:
		hud.set_goal("ALL WORLDS UNLOCKED!")


func _on_milestone(world_id: String) -> void:
	var widx := 0
	for i in Game.WORLDS.size():
		if Game.WORLDS[i]["id"] == world_id:
			widx = i
	Game.current_world = widx
	Game.save_game()
	Audio.play_sfx("res://assets/audio/sfx_levelup.wav")
	hud.show_toast("NEW WORLD UNLOCKED: %s!" % Game.WORLDS[widx]["name"])
	await get_tree().create_timer(1.8).timeout
	get_tree().reload_current_scene()


func _on_skin_unlocked(skin_id: String) -> void:
	Audio.play_sfx("res://assets/audio/sfx_unlock.wav")
	hud.show_toast("SKIN UNLOCKED: %s (choose it in SKINS)" % skin_id.capitalize())


func _on_player_died() -> void:
	Audio.play_sfx("res://assets/audio/sfx_hurt.wav", 0.6, 0.7, -2.0)
	hud.show_game_over(Game.run_coins)

