extends CharacterBody2D
## Player controller: run, sprint, jump, stomp enemies, take damage, skins.

signal died

const SPEED := 95.0
const SPRINT := 145.0
const JUMP_VELOCITY := -265.0
const GRAVITY := 780.0
const INVULN_TIME := 1.2

const FRAME_COUNTS := {"idle": 2, "walk": 4, "run": 4, "jump": 2}
const ANIM_SPEED := {"idle": 2.0, "walk": 9.0, "run": 12.0, "jump": 5.0}

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D

var facing := 1
var invuln := 0.0
var hp := 3
var max_hp := 3
var dead := false
var skin_id := "hero"


func _ready() -> void:
	add_to_group("player")
	set_skin(Game.current_skin)


func set_skin(sid: String) -> void:
	skin_id = sid
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	for anim in FRAME_COUNTS.keys():
		var tex: Texture2D = load("res://assets/sprites/player/%s_%s.png" % [skin_id, anim])
		var n: int = FRAME_COUNTS[anim]
		var fw := int(tex.get_width() / float(n))
		sf.add_animation(anim)
		for i in range(n):
			var atlas := AtlasTexture.new()
			atlas.atlas = tex
			atlas.region = Rect2(i * fw, 0, fw, tex.get_height())
			sf.add_frame(anim, atlas)
		sf.set_animation_loop(anim, anim != "jump")
		sf.set_animation_speed(anim, ANIM_SPEED[anim])
	sprite.sprite_frames = sf
	sprite.play("idle")


func _unhandled_input(event: InputEvent) -> void:
	if dead and event.is_action_pressed("restart"):
		get_tree().reload_current_scene()


func _physics_process(delta: float) -> void:
	if dead:
		return
	if not is_on_floor():
		velocity.y += GRAVITY * delta
	elif velocity.y > 0.0:
		velocity.y = 20.0

	var dir := Input.get_axis("move_left", "move_right")
	var sprint := Input.is_key_pressed(KEY_SHIFT)
	var target := dir * (SPRINT if sprint and dir != 0.0 else SPEED)
	velocity.x = lerp(velocity.x, target, 0.25 if is_on_floor() else 0.12)
	if dir != 0.0:
		facing = 1 if dir > 0.0 else -1
		sprite.flip_h = facing < 0

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY
		GameStats.jumps += 1
		Audio.play_sfx("res://assets/audio/sfx_jump.wav", 0.95, 1.05)

	_update_anim(sprint)
	move_and_slide()

	if invuln > 0.0:
		invuln -= delta
		modulate.a = 0.45 if int(invuln * 14.0) % 2 == 0 else 1.0
		if invuln <= 0.0:
			modulate.a = 1.0

	if global_position.y > 600.0:
		take_damage(hp)


func _update_anim(sprint: bool) -> void:
	var a := "idle"
	if not is_on_floor():
		a = "jump"
	elif absf(velocity.x) > 20.0:
		a = "run" if sprint else "walk"
	if sprite.animation != a:
		sprite.play(a)


func take_damage(amount := 1) -> void:
	if invuln > 0.0 or dead:
		return
	hp -= amount
	invuln = INVULN_TIME
	Audio.play_sfx("res://assets/audio/sfx_hurt.wav")
	if hp <= 0:
		die()
	else:
		var tw := create_tween()
		tw.tween_property(sprite, "modulate", Color(1, 0.35, 0.35, 1), 0.09)
		tw.tween_property(sprite, "modulate", Color(1, 1, 1, 1), 0.15)


func die() -> void:
	if dead:
		return
	dead = true
	Game.lose_run_coins()
	Game.save_game()
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", PI * 2, 0.4)
	tw.parallel().tween_property(self, "modulate:a", 0.0, 0.6)
	set_physics_process(false)
	collision_layer = 0
	died.emit()


func heal(n := 1) -> void:
	hp = mini(hp + n, max_hp)


func bounce() -> void:
	velocity.y = JUMP_VELOCITY * 0.75

