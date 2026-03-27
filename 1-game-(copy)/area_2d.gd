






extends Area2D # Use Area3D for 3D games

@export var jump_force: float = -800.0 # Negative for upward in 2D

func _on_body_entered(body):
	# Check if the body entering is the player (adjust "Player" to your class name)
	if body is CharacterBody2D: 
		# Apply the jump force to the player's velocity
		body.velocity.y = jump_force
		
		# Optional: Play an animation if you have one
		if has_node("AnimationPlayer"):
			$AnimationPlayer.play("activate")
