extends CharacterBody2D

const SPEED      =  200.0
const FLAP_FORCE = -450.0

@onready var _sprite := $AnimatedSprite2D


func _ready() -> void:
	_sprite.stop()
	_sprite.frame = 2   # resting "level" frame


func _physics_process(delta: float) -> void:
	velocity += get_gravity() * delta
	velocity.x = SPEED

	if Input.is_action_just_pressed("ui_accept"):
		velocity.y = FLAP_FORCE
		_sprite.play("default")

	# Return to resting frame once the one-shot animation finishes
	if not _sprite.is_playing():
		_sprite.frame = 2

	move_and_slide()
