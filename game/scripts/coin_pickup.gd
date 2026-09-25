extends Area2D
## Loose coin popped from enemies; magnetised toward the player.

var velocity := Vector2.ZERO
var value := 1
var age := 0.0
const LIFE := 14.0


func _ready() -> void:
	collision_layer = 4
	collision_mask = 2
	monitoring = true
	monitorable = false
	add_to_group("pickups")
	var col := CollisionShape2D.new()
	var sh := CircleShape2D.new()
	sh.radius = 8.0
	col.shape = sh
	add_child(col)
	body_entered.connect(_on_touch)
	var tex: Texture2D = load(Game.WORLDS[Game.current_world]["coin_tex"])
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
	sf.set_animation_speed("spin", 10.0)
	var a := AnimatedSprite2D.new()
	a.sprite_frames = sf
	a.play("spin")
	add_child(a)


func _physics_process(delta: float) -> void:
	age += delta
	if age > LIFE:
		queue_free()
		return
	velocity.y += 700.0 * delta
	var p := get_tree().get_first_node_in_group("player") as Node2D
	if p != null:
		var d := p.global_position - global_position
		if d.length() < 70.0 and age > 0.25:
			velocity += d.normalized() * 950.0 * delta
	global_position += velocity * delta
	var space := get_world_2d().direct_space_state
	var q := PhysicsPointQueryParameters2D.new()
	q.position = global_position + Vector2(0, 6)
	q.collision_mask = 1
	if not space.intersect_point(q, 1).is_empty() and velocity.y > 0.0:
		velocity.y = -velocity.y * 0.35
		velocity.x *= 0.7


func _on_touch(body: Node2D) -> void:
	if body.is_in_group("player"):
		Game.add_coin(value)
		Audio.play_sfx("res://assets/audio/sfx_coin.wav", 0.95, 1.15, -8.0)
		queue_free()

