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
 var routes=[[[38,36],[38,29],[33,26],[33,20],[38,17]],[[38,29],[43,26],[43,20],[38,17]]]
 for route in routes:
  for i in range(route.size()-1):
   var a=Vector3(route[i][0],1.1,route[i][1]);var b=Vector3(route[i+1][0],1.1,route[i+1][1])
   for j in range(17):
    var p=a.lerp(b,j/16.0);samples+=1
    var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.transform=Transform3D(Basis(),p);q.collision_mask=11
    var hits=space.intersect_shape(q,4)
    if hits:failures.append('Blocked route '+str(p)+': '+str(hits[0].collider.get_path()))
    var floor_hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(p,Vector3(p.x,-1,p.z),11))
    var floor_y=.07 if p.z>=33 else 0.0
    if not floor_hit or abs(floor_hit.position.y-floor_y)>.03:failures.append('Uneven/missing lawn '+str(p))
 for x in [30.5,45.5]:
  for z in [17,18,19]:
   var expected=.6 if z!=18 else 1.07
   var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,2,z),Vector3(x,-.5,z),11))
   if not hit or abs(hit.position.y-expected)>.025:failures.append('Missing table/seat support '+str(Vector2(x,z)))
 print('Gate picnic physics: ',samples,' route capsules/floors; 6 table/seat rays')
 for failure in failures:print('FAIL: ',failure)
 print('PASS' if failures.is_empty() else 'FAILED')
 scene.queue_free()
 for i in range(3):await process_frame
 quit(0 if failures.is_empty() else 1)
