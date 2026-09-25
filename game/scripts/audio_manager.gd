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

