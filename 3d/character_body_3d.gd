extends CharacterBody3D

const SPEED = 5.0
const DASH_SPEED = 20.0
const JUMP_VELOCITY = 7.1

var sprint = 2.5
var shop = false

@export var stamina_bar: ProgressBar
var max_stamina = 50.0
var stamina = 50.0
var drain = 30.0   
var regen = 5.0   

@export var dash_stamina_cost := 20.0
@export var dash_duration := 0.2     
@export var dash_cooldown := 0.5     

var is_dashing := false
var dash_timer := 0.0
var cooldown_timer := 0.0
var dash_direction := Vector3.ZERO


func _physics_process(delta: float) -> void:
	if cooldown_timer > 0:
		cooldown_timer -= delta
		
	if is_dashing:
		dash_timer -= delta
		if dash_timer <= 0:
			is_dashing = false 

	if not is_on_floor() and not is_dashing:
		velocity += get_gravity() * delta

	if Input.is_action_just_pressed("ui_accept") and is_on_floor() and not is_dashing:
		velocity.y = JUMP_VELOCITY

	var input_dir := Input.get_vector("ui_up", "ui_down", "ui_right", "ui_left")
	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

	if Input.is_action_just_pressed("dash") and not is_dashing and cooldown_timer <= 0 and stamina >= dash_stamina_cost:
		is_dashing = true
		dash_timer = dash_duration
		cooldown_timer = dash_cooldown
		stamina -= dash_stamina_cost
		
		if direction == Vector3.ZERO:
			dash_direction = -transform.basis.z 
		else:
			dash_direction = direction

	var current_speed = SPEED
	
	if stamina == 0:
		
	
	if is_dashing:
		velocity.x = dash_direction.x * DASH_SPEED
		velocity.z = dash_direction.z * DASH_SPEED
	else:
		if Input.is_action_pressed("sprint") and direction and stamina > 0:
			current_speed = SPEED * sprint
			stamina -= drain * delta
		else:
			stamina += regen * delta
			
		if direction:
			velocity.x = direction.x * current_speed
			velocity.z = direction.z * current_speed
		else:
			velocity.x = move_toward(velocity.x, 0, current_speed)
			velocity.z = move_toward(velocity.z, 0, current_speed)

	stamina = clamp(stamina, 0, max_stamina)
	if stamina_bar:
		stamina_bar.max_value = max_stamina
		stamina_bar.value = stamina

	move_and_slide()


func _on_area_3d_body_shape_entered(body_rid: RID, body: Node3D, body_shape_index: int, local_shape_index: int) -> void:
	get_tree().reload_current_scene()


func _on_area_3d_2_body_shape_entered(body_rid: RID, body: Node3D, body_shape_index: int, local_shape_index: int) -> void:
	velocity.y = 20


func _on_tot_body_shape_entered(body_rid: RID, body: Node3D, body_shape_index: int, local_shape_index: int) -> void:
	get_tree().reload_current_scene()


func _on_area_3d_3_body_shape_entered(body_rid: RID, body: Node3D, body_shape_index: int, local_shape_index: int) -> void:
	get_tree().change_scene_to_file("shop.tscn")
