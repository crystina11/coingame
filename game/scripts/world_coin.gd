extends Node2D
## Static coin placed by the level generator. Gems use custom_tex.

@export var value := 1
@export var custom_tex := ""    # if set, overrides world coin strip
var bob_t := 0.0
var base_y := 0.0
var taken := false


func _ready() -> void:
	var area := Area2D.new()
	area.collision_layer = 4
	area.collision_mask = 2
	area.monitorable = false
	add_child(area)
	var col := CollisionShape2D.new()
	var sh := CircleShape2D.new()
	sh.radius = 10.0
	col.shape = sh
	area.add_child(col)
	area.body_entered.connect(_on_touch)

	var path: String = custom_tex if custom_tex != "" else Game.WORLDS[Game.current_world]["coin_tex"]
	var tex: Texture2D = load(path)
	if custom_tex != "":
		var sp := Sprite2D.new()
		sp.texture = tex
		add_child(sp)
	else:
		var n := int(round(tex.get_width() / 12.0))
		var sf := SpriteFrames.new()
		sf.remove_animation("default")
		sf.add_animation("spin")
		for i in range(n):
			var atlas := AtlasTexture.new()
			atlas.atlas = tex
			atlas.region = Rect2(i * 12, 0, 12, 12)
			sf.add_frame("spin", atlas)
		sf.set_animation_loop("spin", true)
		sf.set_animation_speed("spin", 9.0)
		var a := AnimatedSprite2D.new()
		a.sprite_frames = sf
		a.play("spin")
		add_child(a)
	base_y = position.y
	bob_t = randf() * TAU


func _process(delta: float) -> void:
	bob_t += delta * 3.0
	position.y = base_y + sin(bob_t) * 2.5


func _on_touch(body: Node2D) -> void:
	if taken:
		return
	if body.is_in_group("player"):
		taken = true
		Game.add_coin(value)
		Audio.play_sfx("res://assets/audio/sfx_coin.wav", 0.95, 1.15, -8.0)
		FloatingText.spawn(get_parent(), position - Vector2(6, 18), "+%d" % value,
			Color(1, 0.9, 0.4) if value < 10 else Color(0.5, 0.9, 1))
		var tw := create_tween()
		tw.tween_property(self, "scale", Vector2(1.7, 1.7), 0.08)
		tw.tween_interval(0.02)
		tw.tween_callback(queue_free)
		set_process(false)

