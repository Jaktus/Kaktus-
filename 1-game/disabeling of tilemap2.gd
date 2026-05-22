
extends Area2D

# Greift auf den TileMapLayer2 zu, der unter der Area2D liegt
@onready var tilemap = $TileMapLayer2

func _ready() -> void:
	# Verbindet die Signale automatisch per Code
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: CharacterBody2D) -> void:



	tilemap.enabled = false 
