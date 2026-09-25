#!/usr/bin/env python3
"""Writes all GDScript files for the game with proper tab indentation."""
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "game", "scripts")
os.makedirs(ROOT, exist_ok=True)


def w(name: str, text: str):
    # convert 4-space indents (and continuation lines starting with '>' marker) to tabs
    lines = []
    for ln in text.split("\n"):
        if ln.startswith(">"):          # explicit continuation line -> extra tab
            body = ln[1:]
            n = len(body) - len(body.lstrip(" "))
            lines.append("\t" * (n // 4 + 1) + body.strip())
        else:
            n = len(ln) - len(ln.lstrip(" "))
            lines.append("\t" * (n // 4) + ln[n:])
    path = os.path.join(ROOT, name)
    with open(path, "w") as f:
        f.write("\n".join(lines).lstrip("\n") + "\n")
    print("wrote", name)


# ---------------------------------------------------------------------------
w("game.gd", """
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
""")

# ---------------------------------------------------------------------------
w("audio_manager.gd", """
extends Node
## Sound manager: looping music + pooled SFX players.

var _sfx_pool: Array[AudioStreamPlayer] = []
var _music: AudioStreamPlayer
var _current_music := ""


func _ready() -> void:
    _music = AudioStreamPlayer.new()
    add_child(_music)
    for i in 10:
        var p := AudioStreamPlayer.new()
        add_child(p)
        _sfx_pool.append(p)


func play_music(path: String, restart := false) -> void:
    if path == _current_music and not restart:
        if not _music.playing:
            _music.play()
        return
    _current_music = path
    var s: AudioStreamWAV = load(path)
    # loop the whole stream (musical tracks are generated to be seamless)
    s.loop_mode = AudioStreamWAV.LOOP_FORWARD
    var frames := s.data.size() / float(s.mix_rate * s.channels * 2.0)
    s.loop_begin = int(frames * 4.0)          # loop points are in 4-ms ticks
    s.loop_end = int(frames * 4.0)
    _music.stream = s
    _music.volume_db = -10.0
    _music.play()


func stop_music() -> void:
    _music.stop()
    _current_music = ""


func play_sfx(path: String, pitch_min := 1.0, pitch_max := 1.0, vol_db := -6.0) -> void:
    if not ResourceLoader.exists(path):
        return
    for p in _sfx_pool:
        if not p.playing:
            _fire(p, path, pitch_min, pitch_max, vol_db)
            return
    _fire(_sfx_pool[0], path, pitch_min, pitch_max, vol_db)


func _fire(p: AudioStreamPlayer, path: String, pitch_min: float, pitch_max: float, vol_db: float) -> void:
    p.stream = load(path)
    p.pitch_scale = randf_range(pitch_min, pitch_max)
    p.volume_db = vol_db
    p.play()
""")

# ---------------------------------------------------------------------------
w("game_stats.gd", """
extends Node
## Session statistics.

var enemies_stomped: int = 0
var coins_picked_up: int = 0
var jumps: int = 0
var play_time: float = 0.0


func _process(delta: float) -> void:
    play_time += delta
""")

# ---------------------------------------------------------------------------
w("player.gd", """
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
""")

# ---------------------------------------------------------------------------
w("enemy.gd", """
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
""")

# ---------------------------------------------------------------------------
w("coin_pickup.gd", """
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
""")

# ---------------------------------------------------------------------------
w("world_coin.gd", """
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
""")

# ---------------------------------------------------------------------------
w("floating_text.gd", """
class_name FloatingText
extends Node2D
## Spawns floating "+N" text in world space that rises and fades.

static func spawn(parent: Node, pos: Vector2, txt: String, color := Color.WHITE) -> void:
    if parent == null or not is_instance_valid(parent):
        return
    var lbl := Label.new()
    lbl.text = txt
    lbl.z_index = 100
    lbl.add_theme_font_size_override("font_size", 10)
    lbl.add_theme_color_override("font_color", color)
    lbl.add_theme_color_override("font_outline_color", Color(0.1, 0.08, 0.12, 1))
    lbl.add_theme_constant_override("outline_size", 3)
    lbl.position = pos
    parent.add_child(lbl)
    var tw := lbl.create_tween()
    tw.set_parallel(true)
    tw.tween_property(lbl, "position:y", pos.y - 26.0, 0.7).set_ease(Tween.EASE_OUT)
    tw.tween_property(lbl, "modulate:a", 0.0, 0.7).set_delay(0.25).set_ease(Tween.EASE_IN)
    tw.chain().tween_callback(lbl.queue_free)
""")

# ---------------------------------------------------------------------------
w("background.gd", """
extends Node2D
## Gradient sky + parallax hill layers drawn procedurally.

var top_color := Color("6aa8e0")
var bot_color := Color("bfe3f5")
var seed_val := 1337

var _mat: ShaderMaterial

const FRAG := \"\"\"
shader_type canvas_item;
uniform vec4 top_color : source_color;
uniform vec4 bot_color : source_color;
void fragment() {
    COLOR = mix(bot_color, top_color, UV.y);
}
\"\"\"


func _ready() -> void:
    var wdef: Dictionary = Game.WORLDS[Game.current_world]
    top_color = wdef["sky_top"]
    bot_color = wdef["sky_bot"]
    seed_val = 1337 + Game.current_world * 7919
    var shader := Shader.new()
    shader.code_fragment = FRAG
    _mat = ShaderMaterial.new()
    _mat.shader = shader
    _mat.set_shader_parameter("top_color", top_color)
    _mat.set_shader_parameter("bot_color", bot_color)
    var sky := Polygon2D.new()
    sky.polygon = PackedVector2Array([Vector2(-2000, -1000), Vector2(4500, -1000),
        Vector2(4500, 1200), Vector2(-2000, 1200)])
    sky.material = _mat
    add_child(sky)
    _build_hills()


func _build_hills() -> void:
    var rng := RandomNumberGenerator.new()
    rng.seed = seed_val
    var layer_specs := [
        {"y": 240.0, "amp": 60.0, "col": _mix(bot_color, Color(0.35, 0.5, 0.4), 0.55), "step": 90.0, "z": -20},
        {"y": 268.0, "amp": 44.0, "col": _mix(bot_color, Color(0.25, 0.4, 0.3), 0.7), "step": 70.0, "z": -10},
    ]
    for spec in layer_specs:
        var poly := Polygon2D.new()
        poly.color = spec["col"]
        poly.z_index = spec["z"]
        var pts := PackedVector2Array()
        var x := -2000.0
        var phase := rng.randf() * TAU
        while x < 4500.0:
            var y: float = spec["y"] - abs(sin(x * 0.004 + phase)) * spec["amp"] \\
                - sin(x * 0.013 + phase * 2.0) * spec["amp"] * 0.25
            pts.append(Vector2(x, y))
            x += spec["step"]
        pts.append(Vector2(4500, 1200))
        pts.append(Vector2(-2000, 1200))
        poly.polygon = pts
        add_child(poly)


func _mix(a: Color, b: Color, t: float) -> Color:
    return a.lerp(b, t)
""")

# ---------------------------------------------------------------------------
w("level_gen.gd", """
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
""")



# ---------------------------------------------------------------------------
w("level.gd", """
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
""")


# ---------------------------------------------------------------------------
w("hud.gd", """
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
    s.text = "You dropped %d run coins.\nLifetime total is safe: %d" % [dropped, Game.total_coins]
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
""")


# ---------------------------------------------------------------------------
w("main_menu.gd", """
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
    _toast("\n".join(lines))


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
""")


# ---------------------------------------------------------------------------
w("skins_menu.gd", """
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
""")

print("all scripts written")
