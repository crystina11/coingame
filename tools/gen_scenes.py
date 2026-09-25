#!/usr/bin/env python3
"""Writes all Godot .tscn scene files for the game (text format, no editor needed)."""
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "game", "scenes")
os.makedirs(ROOT, exist_ok=True)


def w(name: str, text: str):
    path = os.path.join(ROOT, name)
    with open(path, "w", newline="\n") as f:
        f.write(text.lstrip("\n"))
    print("wrote", name)


# ---------------------------------------------------------------------------
w("player.tscn", """
[gd_scene load_steps=4 format=3 uid="uid://cc0player1"]

[ext_resource type="Script" path="res://scripts/player.gd" id="1_pl"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_body"]
size = Vector2(10, 18)

[sub_resource type="CircleShape2D" id="CircleShape2D_stomp"]
radius = 9.0

[node name="Player" type="CharacterBody2D"]
collision_layer = 2
collision_mask = 1
script = ExtResource("1_pl")

[node name="AnimatedSprite2D" type="AnimatedSprite2D" parent="."]
position = Vector2(0, -2)

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
position = Vector2(0, -1)
shape = SubResource("RectangleShape2D_body")

[node name="StompArea" type="Area2D" parent="."]
collision_layer = 0
collision_mask = 8

[node name="CollisionShape2D" type="CollisionShape2D" parent="StompArea"]
position = Vector2(0, 6)
shape = SubResource("CircleShape2D_stomp")

[node name="Camera2D" type="Camera2D" parent="."]
position_smoothing_enabled = true
position_smoothing_speed = 6.0
""")

# ---------------------------------------------------------------------------
w("enemy.tscn", """
[gd_scene load_steps=3 format=3 uid="uid://cc0enemy01"]

[ext_resource type="Script" path="res://scripts/enemy.gd" id="1_en"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hit"]
size = Vector2(14, 11)

[node name="Enemy" type="CharacterBody2D"]
collision_layer = 8
collision_mask = 1
script = ExtResource("1_en")

[node name="AnimatedSprite2D" type="AnimatedSprite2D" parent="."]
position = Vector2(0, -2)

[node name="HitArea" type="Area2D" parent="."]
collision_layer = 0
collision_mask = 2

[node name="CollisionShape2D" type="CollisionShape2D" parent="HitArea"]
position = Vector2(0, -2)
shape = SubResource("RectangleShape2D_hit")
""")

# ---------------------------------------------------------------------------
w("world_coin.tscn", """
[gd_scene load_steps=2 format=3 uid="uid://cc0coin001"]

[ext_resource type="Script" path="res://scripts/world_coin.gd" id="1_wc"]

[node name="WorldCoin" type="Node2D"]
script = ExtResource("1_wc")
""")

# ---------------------------------------------------------------------------
w("hud.tscn", """
[gd_scene load_steps=5 format=3 uid="uid://cc0hud0001"]

[ext_resource type="Script" path="res://scripts/hud.gd" id="1_hud"]
[ext_resource type="Texture2D" path="res://assets/sprites/ui/coin_icon.png" id="2_ci"]
[ext_resource type="Texture2D" path="res://assets/sprites/ui/heart.png" id="3_hb"]
[ext_resource type="Texture2D" path="res://assets/sprites/ui/heart_empty.png" id="4_he"]

[node name="HUD" type="CanvasLayer"]
script = ExtResource("1_hud")

[node name="TopBar" type="Control" parent="."]
layout_mode = 3
anchors_preset = 10
anchor_right = 1.0
offset_bottom = 40.0
mouse_filter = 2

[node name="Panel" type="Panel" parent="TopBar"]
self_modulate = Color(0.08, 0.07, 0.12, 0.55)
layout_mode = 1
anchors_preset = 10
anchor_right = 1.0
offset_bottom = 26.0
mouse_filter = 2

[node name="CoinIcon" type="TextureRect" parent="TopBar"]
layout_mode = 0
offset_left = 6.0
offset_top = 5.0
offset_right = 18.0
offset_bottom = 17.0
texture = ExtResource("2_ci")
stretch_mode = 4

[node name="CoinLabel" type="Label" parent="TopBar"]
layout_mode = 0
offset_left = 22.0
offset_top = 5.0
offset_right = 140.0
offset_bottom = 19.0
theme_override_font_sizes/font_size = 12
text = "0"
vertical_alignment = 1

[node name="GoalLabel" type="Label" parent="TopBar"]
layout_mode = 1
anchors_preset = 5
anchor_left = 0.5
anchor_right = 0.5
offset_left = -120.0
offset_top = 5.0
offset_right = 120.0
offset_bottom = 19.0
theme_override_font_sizes/font_size = 10
horizontal_alignment = 1
text = "NEXT WORLD: 100"

[node name="HeartsBox" type="HBoxContainer" parent="TopBar"]
layout_mode = 1
anchors_preset = 2
anchor_left = 1.0
anchor_right = 1.0
offset_left = -84.0
offset_top = 4.0
offset_right = -6.0
offset_bottom = 20.0
alignment = 2

[node name="RunLabel" type="Label" parent="TopBar"]
layout_mode = 0
offset_left = 150.0
offset_top = 6.0
offset_right = 320.0
offset_bottom = 18.0
theme_override_colors/font_color = Color(0.85, 0.85, 0.95, 0.85)
theme_override_font_sizes/font_size = 9
text = "carrying: 0"

[node name="Toast" type="Label" parent="."]
visible = false
layout_mode = 1
anchors_preset = 5
anchor_left = 0.5
anchor_right = 0.5
offset_left = -220.0
offset_top = 44.0
offset_right = 220.0
offset_bottom = 64.0
theme_override_colors/font_color = Color(1, 0.95, 0.7, 1)
theme_override_font_sizes/font_size = 12
horizontal_alignment = 1
text = "toast"

[node name="Hint" type="Label" parent="."]
layout_mode = 1
anchors_preset = 12
anchor_top = 1.0
anchor_right = 1.0
anchor_bottom = 1.0
offset_top = -18.0
theme_override_colors/font_color = Color(1, 1, 1, 0.55)
theme_override_font_sizes/font_size = 8
horizontal_alignment = 1
text = "A/D or arrows: move   Space/W: jump   Shift: sprint   R: restart   ESC: menu"
""")

# ---------------------------------------------------------------------------
w("level.tscn", """
[gd_scene load_steps=6 format=3 uid="uid://cc0level0001"]

[ext_resource type="Script" path="res://scripts/level.gd" id="1_lvl"]
[ext_resource type="PackedScene" path="res://scenes/player.tscn" id="2_pl"]
[ext_resource type="Script" path="res://scripts/level_gen.gd" id="3_gen"]
[ext_resource type="PackedScene" path="res://scenes/hud.tscn" id="4_hud"]
[ext_resource type="Script" path="res://scripts/background.gd" id="5_bg"]

[node name="Level" type="Node2D"]
script = ExtResource("1_lvl")

[node name="Background" type="Node2D" parent="."]
z_index = -30
script = ExtResource("5_bg")

[node name="World" type="Node2D" parent="."]

[node name="Terrain" type="TileMapLayer" parent="World"]

[node name="Deco" type="Node2D" parent="World"]

[node name="Coins" type="Node2D" parent="World"]

[node name="Enemies" type="Node2D" parent="World"]

[node name="PlayerSpawn" type="Marker2D" parent="World"]

[node name="LevelGen" type="Node2D" parent="World"]
script = ExtResource("3_gen")

[node name="Player" parent="." instance=ExtResource("2_pl")]
position = Vector2(100, 200)

[node name="HUD" parent="." instance=ExtResource("4_hud")]
""")

# ---------------------------------------------------------------------------
w("main_menu.tscn", """
[gd_scene load_steps=3 format=3 uid="uid://cc0menu0001"]

[ext_resource type="Script" path="res://scripts/main_menu.gd" id="1_mn"]
[ext_resource type="Texture2D" path="res://assets/sprites/ui/logo_coin.png" id="2_lc"]

[node name="MainMenu" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
script = ExtResource("1_mn")

[node name="BG" type="ColorRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
color = Color(0.11, 0.09, 0.16, 1)

[node name="Title" type="Label" parent="."]
layout_mode = 1
anchors_preset = 5
anchor_left = 0.5
anchor_right = 0.5
offset_left = -200.0
offset_top = 34.0
offset_right = 200.0
offset_bottom = 66.0
theme_override_colors/font_color = Color(1, 0.88, 0.4, 1)
theme_override_font_sizes/font_size = 28
horizontal_alignment = 1
text = "COIN COLLECTOR"

[node name="Subtitle" type="Label" parent="."]
layout_mode = 1
anchors_preset = 5
anchor_left = 0.5
anchor_right = 0.5
offset_left = -200.0
offset_top = 66.0
offset_right = 200.0
offset_bottom = 80.0
theme_override_colors/font_color = Color(0.75, 0.75, 0.9, 1)
theme_override_font_sizes/font_size = 11
horizontal_alignment = 1
text = "an incremental pixel adventure - every sprite & sound generated in Python"

[node name="Logo" type="TextureRect" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -24.0
offset_top = -110.0
offset_right = 24.0
offset_bottom = -62.0
texture = ExtResource("2_lc")
stretch_mode = 4

[node name="Buttons" type="VBoxContainer" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -90.0
offset_top = -20.0
offset_right = 90.0
offset_bottom = 90.0
theme_override_constants/separation = 8

[node name="PlayBtn" type="Button" parent="Buttons"]
custom_minimum_size = Vector2(180, 26)
layout_mode = 2
theme_override_font_sizes/font_size = 13
text = "PLAY"

[node name="SkinsBtn" type="Button" parent="Buttons"]
custom_minimum_size = Vector2(180, 26)
layout_mode = 2
theme_override_font_sizes/font_size = 13
text = "SKINS"

[node name="StatsBtn" type="Button" parent="Buttons"]
custom_minimum_size = Vector2(180, 26)
layout_mode = 2
theme_override_font_sizes/font_size = 13
text = "STATS"

[node name="WipeBtn" type="Button" parent="Buttons"]
custom_minimum_size = Vector2(180, 26)
layout_mode = 2
theme_override_font_sizes/font_size = 10
text = "RESET SAVE"

[node name="Footer" type="Label" parent="."]
layout_mode = 1
anchors_preset = 12
anchor_top = 1.0
anchor_right = 1.0
anchor_bottom = 1.0
offset_top = -18.0
theme_override_colors/font_color = Color(0.6, 0.6, 0.7, 1)
theme_override_font_sizes/font_size = 9
horizontal_alignment = 1
text = "Godot 4 - procedural build"
""")

# ---------------------------------------------------------------------------
w("skins.tscn", """
[gd_scene load_steps=2 format=3 uid="uid://cc0skins001"]

[ext_resource type="Script" path="res://scripts/skins_menu.gd" id="1_sk"]

[node name="SkinsMenu" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
script = ExtResource("1_sk")

[node name="BG" type="ColorRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
color = Color(0.11, 0.09, 0.16, 1)

[node name="Title" type="Label" parent="."]
layout_mode = 1
anchors_preset = 5
anchor_left = 0.5
anchor_right = 0.5
offset_left = -160.0
offset_top = 20.0
offset_right = 160.0
offset_bottom = 46.0
theme_override_colors/font_color = Color(1, 0.88, 0.4, 1)
theme_override_font_sizes/font_size = 20
horizontal_alignment = 1
text = "CHOOSE YOUR SKIN"

[node name="Grid" type="GridContainer" parent="."]
layout_mode = 1
anchors_preset = 5
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -170.0
offset_top = -90.0
offset_right = 170.0
offset_bottom = 60.0
theme_override_constants/h_separation = 10
theme_override_constants/v_separation = 10
columns = 3

[node name="BackBtn" type="Button" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -60.0
offset_top = 120.0
offset_right = 60.0
offset_bottom = 146.0
theme_override_font_sizes/font_size = 12
text = "BACK"
""")

print("tscn scenes written")
