extends Node
# Read-only fixture probe. Injected into disposable test copies, never released.
var elapsed := 0.0
var pockets: Array = []
var sample_tick := 0
func _ready():
	pockets = JSON.parse_string(FileAccess.get_file_as_string("user://water-pockets.json"))
func _process(delta):
	elapsed += delta
	if elapsed < 1.0: return
	elapsed = 0.0
	sample_tick += 1
	var birds = get_tree().root.find_children("*Psyduck*", "Node3D", true, false)
	print("WATER_POPULATION ", JSON.stringify({"tick":sample_tick,"count":birds.size()}))
	for bird in birds:
		var p: Vector3 = bird.global_position
		var inside := false
		for pond in pockets:
			var d = pow((p.x-pond[0])/pond[2],2)+pow((p.z-pond[1])/pond[3],2)
			if d <= 1.001 and abs(p.y-0.13) <= 0.6: inside = true
		var bottom_y = null
		var frame = null
		for child in bird.find_children("Body", "Sprite3D", true, false):
			# Reviewed alpha bounds of the five 400-pixel body frames.
			var bottoms = [241, 240, 239, 245, 246]
			frame = child.frame
			if frame >= 0 and frame < bottoms.size():
				bottom_y = child.to_global(Vector3(0, (200-bottoms[frame])*child.pixel_size, 0)).y
		print("WATER_REVIEW ", JSON.stringify({"bird":str(bird.name),"position":[p.x,p.y,p.z],"inside":inside,"body_bottom_y":bottom_y,"frame":frame}))
