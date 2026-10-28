extends Button


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE



func _process(delta: float) -> void:
	if button_pressed:
		get_tree().change_scene_to_file("Game.tscn")
