extends SceneTree
func _initialize():call_deferred("run")
func strip_scripts(n):
 for c in n.get_children():strip_scripts(c)
 n.set_script(null)
func run():
 var packed=load("res://Levels/SafariZone.tscn")
 var scene=packed.instantiate()
 for c in scene.get_children():
  if c.name!="ForestCheckpoint":scene.remove_child(c);c.free()
 var gate=scene.get_node("ForestCheckpoint/ForestStarGate")
 gate.get_parent().remove_child(gate);gate.free()
 strip_scripts(scene);root.add_child(scene)
 for i in range(12):await physics_frame
 var cases=JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
 var space=root.get_world_3d().direct_space_state
 var failures=[]
 for p in cases.fences:
  for y in [.6,1.5,2.7]:
   var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],y,p[1]),Vector3(p[2],y,p[3]),11))
   if not hit:failures.append("Missing fence collision "+str(p)+" height "+str(y))
 var capsule=CapsuleShape3D.new();capsule.radius=.32;capsule.height=1.6
 for p in cases.passage:
  var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.collision_mask=11;q.transform=Transform3D(Basis(),Vector3(p[0],1,p[1]))
  if not space.intersect_shape(q,1).is_empty():failures.append("Blocked gate passage "+str(p))
 for f in failures:print("FAIL: ",f)
 print("Forest boundary: ",cases.fences.size()*3," fence ray checks; ",cases.passage.size()," open-gate capsule samples")
 scene.free();scene=null;packed=null
 for i in range(12):await process_frame
 print("PASS" if failures.is_empty() else "FAILED")
 quit(0 if failures.is_empty() else 1)
