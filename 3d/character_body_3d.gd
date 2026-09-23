extends CharacterBody3D


const SPEED = 5.0
const DASH = 20
var sprint = 2.5
const JUMP_VELOCITY = 6.1

@export var stamina_bar: ProgressBar
var max_stamina = 100.0
var stamina = 100.0
var drain = 30.0   # per second while sprinting
var regen = 15.0   # per second while not sprinting


func _physics_process(delta: float) -> void:
	# Add the gravity.
	if not is_on_floor():
		velocity += get_gravity() * delta

	# Handle jump.
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	# Get the input direction and handle the movement/deceleration.
	var input_dir := Input.get_vector("ui_up", "ui_down", "ui_right", "ui_left")
	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

	var current_speed = SPEED
	if Input.is_action_pressed("sprint") and direction and stamina > 0:
		current_speed = SPEED * sprint
		stamina -= drain * delta
	else:
		stamina += regen * delta
	stamina = clamp(stamina, 0, max_stamina)

	if stamina_bar:
		stamina_bar.max_value = max_stamina
		stamina_bar.value = stamina

	if direction:
		velocity.x = direction.x * current_speed
		velocity.z = direction.z * current_speed
	else:
		velocity.x = move_toward(velocity.x, 0, current_speed)
		velocity.z = move_toward(velocity.z, 0, current_speed)

	move_and_slide()


func _on_area_3d_body_shape_entered(body_rid: RID, body: Node3D, body_shape_index: int, local_shape_index: int) -> void:
	get_tree().reload_current_scene()
