extends CanvasLayer
## In-game HUD: coin counter, hearts, goal banner, toast messages.

@onready var coin_label: Label = $TopBar/CoinLabel
@onready var goal_label: Label = $TopBar/GoalLabel
@onready var run_label: Label = $TopBar/RunLabel
@onready var hearts_box: HBoxContainer = $TopBar/HeartsBox
@onready var toast: Label = $Toast

var _player: Node = null
var _heart_full: Texture2D = preload("res://assets/sprites/ui/heart.png")
var _heart_empty: Texture2D = preload("res://assets/sprites/ui/heart_empty.png")


func setup(player: Node) -> void:
	_player = player
	for i in player.max_hp:
		var t := TextureRect.new()
		t.texture = _heart_full
		t.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
		t.custom_minimum_size = Vector2(14, 14)
		hearts_box.add_child(t)


func _process(_delta: float) -> void:
	if _player == null or not is_instance_valid(_player):
		return
	var kids := hearts_box.get_children()
	for i in kids.size():
		kids[i].texture = _heart_full if i < _player.hp else _heart_empty


func update_coins(total: int, run: int) -> void:
	coin_label.text = str(total)
	run_label.text = "carrying: %d" % run


func set_goal(text: String) -> void:
	goal_label.text = text


var _over: Control = null


func show_game_over(dropped: int) -> void:
	if _over != null:
		return
	_over = ColorRect.new()
	_over.color = Color(0.05, 0.04, 0.08, 0.72)
	_over.set_anchors_preset(Control.PRESET_FULL_RECT)
	var v := VBoxContainer.new()
	v.set_anchors_preset(Control.PRESET_CENTER)
	v.offset_left = -120
	v.offset_top = -50
	v.offset_right = 120
	v.offset_bottom = 50
	v.add_theme_constant_override("separation", 8)
	var t := Label.new()
	t.text = "GAME OVER"
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	t.add_theme_font_size_override("font_size", 22)
	t.add_theme_color_override("font_color", Color(1, 0.45, 0.4))
	v.add_child(t)
	var s := Label.new()
	s.text = "You dropped %d run coins.
Lifetime total is safe: %d" % [dropped, Game.total_coins]
	s.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	s.add_theme_font_size_override("font_size", 10)
	v.add_child(s)
	var b := Button.new()
	b.text = "TRY AGAIN  (R)"
	b.pressed.connect(restart_level)
	v.add_child(b)
	_over.add_child(v)
	add_child(_over)


func restart_level() -> void:
	get_tree().reload_current_scene()


func show_toast(text: String) -> void:
	toast.text = text
	toast.modulate.a = 1.0
	toast.visible = true
	var tw := create_tween()
	tw.tween_interval(2.4)
	tw.tween_property(toast, "modulate:a", 0.0, 0.6)
	tw.tween_callback(func(): toast.visible = false)

