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

