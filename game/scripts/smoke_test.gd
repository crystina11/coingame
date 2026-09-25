extends Node
## Headless smoke test: boots every scene and simulates gameplay logic.

var _label := ""

func _ready() -> void:
    _run()

func _log(msg: String) -> void:
    print("SMOKE: ", msg)

func _run() -> void:
    # --- world 1: meadow
    Game.current_world = 0
    var lvl: Node = load("res://scenes/level.tscn").instantiate()
    get_tree().root.add_child.call_deferred(lvl)
    await get_tree().process_frame
    await get_tree().physics_frame
    await get_tree().physics_frame
    var player: CharacterBody2D = lvl.get_node("Player")
    _log("player skin frames ok: %s" % str(player.sprite.sprite_frames.get_animation_names()))
    var coins: Node = lvl.get_node("World/Coins")
    var enemies: Node = lvl.get_node("World/Enemies")
    _log("coins=%d enemies=%d" % [coins.get_child_count(), enemies.get_child_count()])
    assert(coins.get_child_count() > 50, "too few coins")
    assert(enemies.get_child_count() > 3, "too few enemies")
    # terrain collision present?
    var bodies := 0
    for c in lvl.get_node("World/LevelGen").get_children():
        if c is StaticBody2D:
            bodies += 1
    _log("static bodies=%d" % bodies)
    assert(bodies > 10, "no collision built")
    # simulate coin collection to milestone 100 (snow unlock)
    while Game.total_coins < 100:
        Game.add_coin(5)
    _log("after 100 coins: highest_world=%d unlocked=%s" % [Game.highest_world, str(Game.unlocked_skins)])
    assert(Game.highest_world >= 1)
    assert("ninja" in Game.unlocked_skins and "yeti" in Game.unlocked_skins)
    # push to beach + all skins
    while Game.total_coins < 520:
        Game.add_coin(10)
    _log("after 520: highest_world=%d skins=%d" % [Game.highest_world, Game.unlocked_skins.size()])
    assert(Game.highest_world == 2 and Game.unlocked_skins.size() == 6)
    # damage / stomp / death paths
    player.invuln = 0.0
    player.take_damage(1)
    _log("hp after hit=%d" % player.hp)
    assert(player.hp == 2)
    var slime: CharacterBody2D = enemies.get_child(0)
    slime.stomp(player)
    _log("stomp bounce vy=%.0f" % player.velocity.y)
    player.hp = 1
    player.invuln = 0.0
    player.take_damage(1)
    await get_tree().create_timer(0.8).timeout
    _log("dead=%d deaths=%d run_coins=%d" % [int(player.dead), Game.deaths, Game.run_coins])
    assert(player.dead)
    lvl.queue_free()
    await get_tree().process_frame
    # --- snow & beach level generation
    for w in [1, 2]:
        Game.current_world = w
        var l2: Node = load("res://scenes/level.tscn").instantiate()
        get_tree().root.add_child.call_deferred(l2)
        await get_tree().process_frame
        await get_tree().physics_frame
        await get_tree().physics_frame
        _log("world %d coins=%d enemies=%d" % [w,
            l2.get_node("World/Coins").get_child_count(),
            l2.get_node("World/Enemies").get_child_count()])
        l2.queue_free()
        await get_tree().process_frame
    # --- menus
    var mm: Node = load("res://scenes/main_menu.tscn").instantiate()
    get_tree().root.add_child.call_deferred(mm)
    await get_tree().process_frame
    _log("main menu ok")
    var sk: Node = load("res://scenes/skins.tscn").instantiate()
    get_tree().root.add_child.call_deferred(sk)
    await get_tree().process_frame
    _log("skins grid children=%d" % sk.get_node("Grid").get_child_count())
    assert(sk.get_node("Grid").get_child_count() == 6)
    Game.save_game()
    Game.load_game()
    _log("save roundtrip total=%d skin=%s" % [Game.total_coins, Game.current_skin])
    _log("ALL SMOKE TESTS PASSED")
    get_tree().quit(0)
