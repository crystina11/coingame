extends Control
## Skin picker grid; locked entries show their unlock requirement.

const UNLOCK_FOR := {"hero": 0, "ninja": 25, "yeti": 100, "surfer": 200,
	"robot": 300, "explorer": 500}


func _ready() -> void:
	$BackBtn.pressed.connect(func():
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn"))
	var grid: GridContainer = $Grid
	for sid in Game.ALL_SKINS:
		grid.add_child(_make_card(sid))


func _make_card(sid: String) -> Control:
	var unlocked: bool = sid in Game.unlocked_skins
	var panel := Panel.new()
	panel.custom_minimum_size = Vector2(108, 112)
	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = 6
	v.offset_top = 4
	v.offset_right = -6
	v.offset_bottom = -4
	panel.add_child(v)

	var tex: Texture2D = load("res://assets/sprites/player/%s_idle.png" % sid)
	var fw := int(tex.get_width() / 2.0)
	var atlas := AtlasTexture.new()
	atlas.atlas = tex
	atlas.region = Rect2(0, 0, fw, tex.get_height())
	var icon := TextureRect.new()
	icon.texture = atlas
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	icon.custom_minimum_size = Vector2(0, 48)
	if not unlocked:
		icon.modulate = Color(0.3, 0.3, 0.35, 1)
	v.add_child(icon)

	var name_lbl := Label.new()
	name_lbl.text = sid.capitalize()
	name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_lbl.add_theme_font_size_override("font_size", 11)
	v.add_child(name_lbl)

	var sub := Label.new()
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 8)
	if unlocked:
		sub.text = "selected" if sid == Game.current_skin else "owned"
		sub.add_theme_color_override("font_color", Color(0.7, 1, 0.7))
	else:
		sub.text = "unlock at %d coins" % UNLOCK_FOR[sid]
		sub.add_theme_color_override("font_color", Color(1, 0.6, 0.6))
	v.add_child(sub)

	var btn := Button.new()
	if not unlocked:
		btn.text = "LOCKED"
	elif sid == Game.current_skin:
		btn.text = "EQUIPPED"
	else:
		btn.text = "SELECT"
	btn.disabled = not unlocked or sid == Game.current_skin
	btn.add_theme_font_size_override("font_size", 9)
	btn.pressed.connect(func():
		Game.set_skin(sid)
		Audio.play_sfx("res://assets/audio/sfx_unlock.wav")
		get_tree().reload_current_scene())
	v.add_child(btn)
	return panel

