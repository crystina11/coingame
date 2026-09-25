extends CharacterBody2D
## Enemy: hopping slime or sine-flying bat. Stompable; touches hurt the player.

@export var enemy_type := "slime_green"   # slime_green|slime_ice|slime_sand|slime_king|bat
@export var patrol_speed := 38.0

const GRAVITY := 780.0
const HOP_VELOCITY := -190.0

var dir := 1
var hop_timer := 0.0
var base_y := 0.0
var t := 0.0
var dead := false
var value := 5

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var area: Area2D = $HitArea


func _ready() -> void:
	add_to_group("enemies")
	var suffix := "fly" if enemy_type == "bat" else "hop"
	var tex: Texture2D = load("res://assets/sprites/enemies/%s_%s.png" % [enemy_type, suffix])
	var n := int(round(tex.get_width() / 16.0))
	var fw := int(tex.get_width() / float(n))
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	sf.add_animation("anim")
	for i in range(n):
		var atlas := AtlasTexture.new()
		atlas.atlas = tex
		atlas.region = Rect2(i * fw, 0, fw, tex.get_height())
		sf.add_frame("anim", atlas)
	sf.set_animation_loop("anim", true)
	sf.set_animation_speed("anim", 6.0 if enemy_type != "bat" else 12.0)
	sprite.sprite_frames = sf
	sprite.play("anim")
	area.body_entered.connect(_on_hit)
	base_y = global_position.y
	match enemy_type:
		"slime_ice":
			patrol_speed = 46.0
		"slime_sand":
			patrol_speed = 55.0
		"slime_king":
			patrol_speed = 30.0
			value = 50
			scale = Vector2(1.6, 1.6)
	hop_timer = randf_range(0.0, 1.0)


func _unhandled_input(event: InputEvent) -> void:
	if dead and event.is_action_pressed("restart"):
		get_tree().reload_current_scene()


func _physics_process(delta: float) -> void:
	if dead:
		return
	t += delta
	if enemy_type == "bat":
		velocity = Vector2(dir * patrol_speed * 1.4, 0)
		global_position.y = base_y + sin(t * 3.2) * 26.0
		if is_on_wall():
			dir *= -1
	else:
		if not is_on_floor():
			velocity.y += GRAVITY * delta
		hop_timer -= delta
		if hop_timer <= 0.0 and is_on_floor():
			velocity.y = HOP_VELOCITY
			hop_timer = randf_range(0.9, 1.6)
		velocity.x = dir * patrol_speed
		if is_on_wall() or (is_on_floor() and not _edge_ahead()):
			dir *= -1
	sprite.flip_h = dir < 0
	move_and_slide()


func _edge_ahead() -> bool:
	var space := get_world_2d().direct_space_state
	var shape := RectangleShape2D.new()
	shape.size = Vector2(2, 14)
	var q := PhysicsShapeQueryParameters2D.new()
	q.shape = shape
	q.transform = Transform2D(0, global_position + Vector2(dir * 20, 10))
	q.collision_mask = 1
	q.exclude = [self]
	return not space.intersect_shape(q, 1).is_empty()


func _on_hit(body: Node2D) -> void:
	if dead:
		return
	var p := body as CharacterBody2D
	if p == null or not p.is_in_group("player") or p.dead:
		return
	if p.velocity.y > 40.0 and p.global_position.y < global_position.y - 6.0:
		stomp(p)
	else:
		p.take_damage(2 if enemy_type == "slime_king" else 1)


func stomp(p: CharacterBody2D) -> void:
	dead = true
	p.bounce()
	Audio.play_sfx("res://assets/audio/sfx_stomp.wav")
	GameStats.enemies_stomped += 1
	FloatingText.spawn(get_parent(), global_position - Vector2(8, 16), "+%d" % value,
		Color(1, 0.9, 0.4))
	for i in range(value):
		var c := preload("res://scripts/coin_pickup.gd").new()
		c.position = global_position + Vector2(randf_range(-8, 8), -6)
		c.velocity = Vector2(randf_range(-70, 70), randf_range(-170, -60))
		get_parent().add_child.call_deferred(c)
	var tw := create_tween()
	tw.tween_property(self, "scale", Vector2.ZERO, 0.18)
	tw.tween_callback(queue_free)

