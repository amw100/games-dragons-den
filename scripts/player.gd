class_name Player
extends CharacterBody2D

const SPEED          =  200.0
const FLAP_FORCE     = -450.0
const DEATH_TIME_SEC =    2.0

var _dead        := false
var _can_restart := false

@onready var _sprite : AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	_sprite.stop()
	_sprite.frame = 2


func _physics_process(delta: float) -> void:
	if _dead:
		velocity += get_gravity() * delta
		move_and_slide()
		return

	velocity += get_gravity() * delta
	velocity.x = SPEED

	if Input.is_action_just_pressed("ui_accept"):
		velocity.y = FLAP_FORCE
		_sprite.play("default")

	if not _sprite.is_playing():
		_sprite.frame = 2

	move_and_slide()


func _input(event: InputEvent) -> void:
	if _can_restart and event.is_pressed() and not event.is_echo():
		get_tree().reload_current_scene()


func die() -> void:
	if _dead:
		return
	_dead = true
	velocity.x = 0.0
	_sprite.play("death")
	await get_tree().create_timer(DEATH_TIME_SEC).timeout
	_can_restart = true
