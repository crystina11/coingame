extends Node2D
## Gradient sky + parallax hill layers drawn procedurally.

var top_color := Color("6aa8e0")
var bot_color := Color("bfe3f5")
var seed_val := 1337

var _mat: ShaderMaterial

const FRAG := """
shader_type canvas_item;
uniform vec4 top_color : source_color;
uniform vec4 bot_color : source_color;
void fragment() {
	COLOR = mix(bot_color, top_color, UV.y);
}
"""


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
			var y: float = spec["y"] - abs(sin(x * 0.004 + phase)) * spec["amp"] \
				- sin(x * 0.013 + phase * 2.0) * spec["amp"] * 0.25
			pts.append(Vector2(x, y))
			x += spec["step"]
		pts.append(Vector2(4500, 1200))
		pts.append(Vector2(-2000, 1200))
		poly.polygon = pts
		add_child(poly)


func _mix(a: Color, b: Color, t: float) -> Color:
	return a.lerp(b, t)

