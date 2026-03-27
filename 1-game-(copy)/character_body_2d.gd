extends CharacterBody2D

@export var speed: float = 300.0
@export var jump_velocity: float = -400.0
@export var coyote_time_duration: float = 0.3
@export var max_luftspruenge: int = 1

var coyote_timer: float = 0.0
var luftsprung_counter: int = 0

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity += get_gravity() * delta
		coyote_timer -= delta
	else:
		coyote_timer = coyote_time_duration
		luftsprung_counter = max_luftspruenge 

	if Input.is_action_just_pressed("ui_accept"):

		if coyote_timer > 0.0:
			velocity.y = jump_velocity
			coyote_timer = 0.0

		elif luftsprung_counter > 0:
			velocity.y = jump_velocity
			luftsprung_counter -= 1

	var direction := Input.get_axis("ui_left", "ui_right")
	if direction:
		velocity.x = direction * speed
		
	else:
		velocity.x = move_toward(velocity.x, 0, speed)

	move_and_slide()
