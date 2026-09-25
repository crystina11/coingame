extends Control
## Main menu: play / skins / stats / reset save.


func _ready() -> void:
	Audio.play_music(Game.WORLDS[Game.highest_world]["music"])
	$Buttons/PlayBtn.pressed.connect(func():
		Game.current_world = Game.highest_world
		Game.save_game()
		get_tree().change_scene_to_file("res://scenes/level.tscn"))
	$Buttons/SkinsBtn.pressed.connect(func():
		get_tree().change_scene_to_file("res://scenes/skins.tscn"))
	$Buttons/StatsBtn.pressed.connect(_show_stats)
	$Buttons/WipeBtn.pressed.connect(_wipe)
	$Buttons/PlayBtn.text = "PLAY   (best run: %d coins)" % Game.best_run


func _show_stats() -> void:
	Audio.play_sfx("res://assets/audio/sfx_click.wav")
	var lines := [
		"lifetime coins: %d" % Game.total_coins,
		"best run: %d" % Game.best_run,
		"deaths: %d" % Game.deaths,
		"world reached: %s" % Game.WORLDS[Game.highest_world]["name"],
		"skins unlocked: %d / %d" % [Game.unlocked_skins.size(), Game.ALL_SKINS.size()],
		"",
		"this session:",
		"  coins picked: %d" % GameStats.coins_picked_up,
		"  enemies stomped: %d" % GameStats.enemies_stomped,
		"  jumps: %d" % GameStats.jumps,
		"  play time: %d s" % int(GameStats.play_time),
	]
	_toast("
".join(lines))


func _wipe() -> void:
	Audio.play_sfx("res://assets/audio/sfx_click.wav")
	Game.reset_save()
	_toast("Save reset. Start collecting again!")


func _toast(text: String) -> void:
	var lbl := Label.new()
	lbl.text = text
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.add_theme_font_size_override("font_size", 10)
	lbl.add_theme_color_override("font_color", Color(1, 0.95, 0.7))
	lbl.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	lbl.offset_left = -170
	lbl.offset_top = 90
	lbl.offset_right = 170
	lbl.offset_bottom = 230
	add_child(lbl)
	var tw := lbl.create_tween()
	tw.tween_interval(3.2)
	tw.tween_property(lbl, "modulate:a", 0.0, 0.5)
	tw.tween_callback(lbl.queue_free)

