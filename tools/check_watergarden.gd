extends SceneTree
func _initialize():call_deferred('run')
func clean(n):
 for c in n.get_children():
  var s=c.get_script()
  if s!=null and str(s.resource_path).ends_with('FreeOnReady.cs'):
   n.remove_child(c);c.free()
  else:clean(c)
 n.set_script(null)
func run():
 var scene=load('res://Levels/SafariZone.tscn').instantiate();clean(scene);root.add_child(scene)
 for i in range(12):await physics_frame
 var space=root.get_world_3d().direct_space_state
 var failures=[];var samples=0
 var capsule=CapsuleShape3D.new();capsule.radius=.35;capsule.height=1.8
 # Whole dry passage, both open entrances, and approach from the main trail.
 var points=[]
 for x in range(50,75):
  for z in [62.0,63.0,64.0]:points.append(Vector3(x,1.2,z))
 for x in range(42,53):points.append(Vector3(x,1.2,66))
 for p in points:
  samples+=1
  var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.transform=Transform3D(Basis(),p);q.collision_mask=11
  var hits=space.intersect_shape(q,4)
  if hits:failures.append('Blocked passage '+str(p)+': '+str(hits[0].collider.get_path()))
  var floor_hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(p,Vector3(p.x,-1,p.z),11))
  if not floor_hit or floor_hit.position.y<-.05:failures.append('Missing floor '+str(p))
 # Continuous collision roof, above player head height, behind the curtain.
 for x in range(54,71):
  var p=Vector3(x,2.5,63)
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(p,p+Vector3(0,2,0),11))
  if not hit or abs(hit.position.y-3.2)>.02:failures.append('Roof clearance '+str(p))
 print('Water garden physics: ',samples,' capsule/floor samples; 17 roof samples')
 for failure in failures:print('FAIL: ',failure)
 print('PASS' if failures.is_empty() else 'FAILED')
 scene.queue_free()
 for i in range(3):await process_frame
 quit(0 if failures.is_empty() else 1)
