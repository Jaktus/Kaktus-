extends Camera2D

@export var target: NodePath
@export var smoothing_speed := 0.5  # Höher = schneller/straffer

var target_node: Node2D

func _ready():
	target_node = get_node(target)
	# Godot's eingebautes Smoothing deaktivieren, wir machen es selbst
	position_smoothing_enabled = true

func _physics_process(delta):
	if target_node:
		global_position = global_position.lerp(target_node.global_position, smoothing_speed * delta)
