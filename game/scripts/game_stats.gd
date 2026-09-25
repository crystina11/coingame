extends Node
## Session statistics.

var enemies_stomped: int = 0
var coins_picked_up: int = 0
var jumps: int = 0
var play_time: float = 0.0


func _process(delta: float) -> void:
	play_time += delta

