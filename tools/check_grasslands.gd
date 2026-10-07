extends SceneTree

func _initialize():
 call_deferred("run")

func strip_scripts(node):
 for child in node.get_children():strip_scripts(child)
 node.set_script(null)

func run():
 var packed=load("res://Levels/SafariZone.tscn")
 if packed==null:quit(1);return
 var scene=packed.instantiate()
 # Exercise real authored meshes/colliders without invoking editor service stubs.
 for child in scene.get_children():
  if child.name!="ReserveFloor" and child.name!="GrasslandsGarden" and not str(child.name).begins_with("GrasslandRowTree") and not str(child.name).begins_with("GrasslandJunctionCherry"):
   scene.remove_child(child);child.free()
 strip_scripts(scene)
 root.add_child(scene)
 for i in range(12):await physics_frame
 var cases=JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
 var failures=[]
 var space=root.get_world_3d().direct_space_state
 var capsule=CapsuleShape3D.new();capsule.radius=.32;capsule.height=1.6
 for p in cases.walk:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],12,p[1]),Vector3(p[0],-2,p[1]),11))
  if not hit:failures.append("Missing walkway at "+str(p));continue
  if abs(hit.position.y-p[2])>.15:failures.append("Wrong walkway height "+str(p)+": "+str(hit.position));continue
  var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.collision_mask=11
  q.transform=Transform3D(Basis(),Vector3(p[0],hit.position.y+.88,p[1]))
  var hits=space.intersect_shape(q,4)
  if not hits.is_empty():failures.append("Blocked elevated route at "+str(p)+": "+str(hits[0].collider.get_path()))
 for p in cases.paths:
  var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.collision_mask=11
  q.transform=Transform3D(Basis(),Vector3(p[0],1.05,p[1]))
  var hits=space.intersect_shape(q,4)
  if not hits.is_empty():failures.append("Blocked grassland path at "+str(p)+": "+str(hits[0].collider.get_path()))
 for p in cases.cliffs:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],15,p[1]),Vector3(p[0],1,p[1]),11))
  if not hit or hit.position.y<5:failures.append("Disconnected cliff spine at "+str(p))
 for p in cases.hedges:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],.6,p[1]-2),Vector3(p[0],.6,p[1]+2),1))
  if not hit:failures.append("Missing hedge collision at "+str(p))
 print("Grasslands physics: ",cases.walk.size()," elevated samples; ",cases.paths.size()," ground-route samples; ",cases.hedges.size()," hedge checks; ",cases.cliffs.size()," connected cliff samples")
 for failure in failures:print("FAIL: ",failure)
 scene.free()
 scene=null;packed=null
 for i in range(12):await process_frame
 print("PASS" if failures.is_empty() else "FAILED")
 quit(0 if failures.is_empty() else 1)
