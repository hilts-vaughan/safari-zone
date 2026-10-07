extends SceneTree
func _initialize():call_deferred("run")
func strip_scripts(n):
 for c in n.get_children():strip_scripts(c)
 n.set_script(null)
func run():
 var packed=load("res://Levels/SafariZone.tscn");var scene=packed.instantiate()
 for c in scene.get_children():
  if c.name!="ForestCheckpoint" and c.name!="ReserveFloor":scene.remove_child(c);c.free()
 strip_scripts(scene);root.add_child(scene)
 for i in range(12):await physics_frame
 var cases=JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
 var space=root.get_world_3d().direct_space_state;var failures=[]
 var capsule=CapsuleShape3D.new();capsule.radius=.32;capsule.height=1.6
 for p in cases.walk:
  # Start below the roof to test the intended walking floor inside the cave.
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],p[2]+.65,p[1]),Vector3(p[0],p[2]-.7,p[1]),11))
  if not hit:failures.append("Missing floor "+str(p));continue
  if abs(hit.position.y-p[2])>.46:failures.append("Wrong floor height "+str(p)+": "+str(hit.position));continue
  var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.collision_mask=11;q.transform=Transform3D(Basis(),Vector3(p[0],hit.position.y+.88,p[1]))
  var hits=space.intersect_shape(q,1)
  if not hits.is_empty():failures.append("Blocked cave route "+str(p)+": "+str(hits[0].collider.get_path()))
 for p in cases.boundary:
  for y in [1.5,4,6]:
   if not space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],y,p[1]),Vector3(p[2],y,p[3]),11)):failures.append("Low cliff gap "+str(p)+" at "+str(y))
 for f in failures:print("FAIL: ",f)
 print("Cave physics: ",cases.walk.size()," floor/clearance samples; ",cases.boundary.size()*3," cliff rays")
 scene.free();scene=null;packed=null
 for i in range(12):await process_frame
 print("PASS" if failures.is_empty() else "FAILED");quit(0 if failures.is_empty() else 1)
