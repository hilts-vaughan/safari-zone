extends SceneTree
func _initialize():
 call_deferred("run")
func run():
 var path="res://EXTERNAL/Touma/SafariZone/Woodland/WoodlandPassage.tscn"
 var packed=load(path)
 if packed==null:
  quit(1);return
 var scene=packed.instantiate()
 var failures=[]
 var terrain=scene.get_node("Escarpments").duplicate()
 root.add_child(terrain)
 for i in range(12):await physics_frame
 var trees=0
 for n in scene.get_node("Planting").get_children():
  if not n.name.begins_with("Tree") and not n.name.begins_with("SkylineTree"):continue
  trees+=1
  var query=PhysicsRayQueryParameters3D.create(Vector3(n.position.x,40,n.position.z),Vector3(n.position.x,-1,n.position.z),11)
  var hit=root.get_world_3d().direct_space_state.intersect_ray(query)
  var expected=hit.position.y+.06 if hit else 0.0
  if abs(n.position.y-expected)>.15:failures.append("Floating or buried tree: "+str(n.name))
 terrain.free()
 root.add_child(scene)
 for i in range(12):await physics_frame
 # A continuous rear escarpment must have rock under every sample on its connecting spine.
 for x in range(-37,36):
  var hit=root.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,30,-29),Vector3(x,4,-29),11))
  if not hit:failures.append("Rock gap at "+str(x)+",-29")
 var capsule=CapsuleShape3D.new();capsule.radius=.32;capsule.height=1.6
 var points=JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
 for p in points:
  var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.transform=Transform3D(Basis(),Vector3(p[0],1.3,p[1]));q.collision_mask=11
  var hits=root.get_world_3d().direct_space_state.intersect_shape(q,4)
  if hits:failures.append("Blocked trail at "+str(p)+": "+str(hits[0].collider.get_path()))
 print("Physics checks: ",points.size()," trail samples, 73 connected-cliff samples, ",trees," grounded trees")
 for failure in failures:print("FAIL: ",failure)
 print("PASS" if failures.is_empty() else "FAILED")
 quit(0 if failures.is_empty() else 1)
