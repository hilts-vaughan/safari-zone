extends SceneTree
func _initialize():call_deferred("run")
func strip(node):
 for child in node.get_children():strip(child)
 node.set_script(null)
func run():
 var packed=load("res://Levels/SafariZone.tscn")
 var scene=packed.instantiate()
 for child in scene.get_children():
  if child.name not in ["ReserveFloor","ReserveSculptedRidges"]:
   scene.remove_child(child);child.free()
 strip(scene);root.add_child(scene)
 for i in range(12):await physics_frame
 var samples=JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
 var space=root.get_world_3d().direct_space_state
 var failures=[]
 for p in samples:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],20,p[1]),Vector3(p[0],-2,p[1]),11))
  if not hit or abs(hit.position.y)>.12:failures.append(str(p))
 print("Sculpted terrain: ",samples.size()," connected-trail ground samples; ",failures.size()," failures")
 for failure in failures:print("FAIL: raised/missing trail ground at ",failure)
 scene.free()
 quit(0 if failures.is_empty() else 1)
