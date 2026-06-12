extends CharacterBody2D

const SPEED = 200.0
const JUMP_VELOCITY = -400.0
const GRAVITY = 980.0
const MAX_JUMPS = 2

const DASH_SPEED = 600.0
const DASH_DURATION := 0.15
const DASH_COOLDOWN := 0.01
const AFTERIMAGE_COUNT := 10
const AFTERIMAGE_INTERVAL := 0.012

@export var after_image_scene: PackedScene

@onready var sprite := $AnimatedSprite2D

var jumps_left := MAX_JUMPS

var is_dashing := false
var dash_timer := 0.0
var dash_cooldown_timer := 0.0
var dash_direction := Vector2.ZERO
var afterimage_timer := 0.0
var afterimages_spawned := 0

func _physics_process(delta):
	if dash_cooldown_timer > 0:
		dash_cooldown_timer -= delta

	if is_dashing:
		dash_timer -= delta
		afterimage_timer -= delta

		if afterimage_timer <= 0 and afterimages_spawned < AFTERIMAGE_COUNT:
			spawn_afterimage()
			afterimage_timer = AFTERIMAGE_INTERVAL
			afterimages_spawned += 1

		velocity = dash_direction * DASH_SPEED

		if dash_timer <= 0:
			is_dashing = false
			velocity = dash_direction * (DASH_SPEED * 0.3)

		move_and_slide()
		return

	if not is_on_floor():
		velocity.y += GRAVITY * delta

	if is_on_floor():
		jumps_left = MAX_JUMPS

	if Input.is_action_just_pressed("ui_accept"):
		if jumps_left > 0:
			velocity.y = JUMP_VELOCITY
			jumps_left -= 1

	if Input.is_action_just_pressed("dash") and dash_cooldown_timer <= 0:
		start_dash()

	var direction = Input.get_axis("ui_left", "ui_right")
	if direction:
		velocity.x = direction * SPEED
		sprite.flip_h = direction < 0
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)

	move_and_slide()

func start_dash():
	var input_dir = Vector2(
		Input.get_axis("ui_left", "ui_right"),
		Input.get_axis("ui_up", "ui_down")
	)

	if input_dir == Vector2.ZERO:
		input_dir.x = 1.0 if not sprite.flip_h else -1.0

	dash_direction = input_dir.normalized()
	is_dashing = true
	dash_timer = DASH_DURATION
	dash_cooldown_timer = DASH_COOLDOWN
	afterimage_timer = 0.0
	afterimages_spawned = 0

func spawn_afterimage():
	if after_image_scene == null:
		return

	var clone = after_image_scene.instantiate()
	get_tree().current_scene.add_child(clone)

	clone.global_position = global_position
	clone.visible = true

	if clone.has_node("AnimatedSprite2D"):
		var clone_sprite = clone.get_node("AnimatedSprite2D")
		clone_sprite.sprite_frames = sprite.sprite_frames
		clone_sprite.animation = sprite.animation
		clone_sprite.frame = sprite.frame
		clone_sprite.flip_h = sprite.flip_h
		clone_sprite.visible = true


func _on_area_2d_4_body_shape_entered(body_rid: RID, body: Node2D, body_shape_index: int, local_shape_index: int) -> void:
	pass # Replace with function body.
