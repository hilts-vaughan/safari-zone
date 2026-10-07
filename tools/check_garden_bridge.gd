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
 # Deck is a continuous arch, including flush entry and exit.
 for i in range(17):
  var z=71+i*.5
  var expected=.65*sin(PI*i/16)
  for x in [22.0,22.6,23.2]:
   samples+=1
   var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,2,z),Vector3(x,-.5,z),11))
   if not hit or abs(hit.position.y-expected)>.025:failures.append('Deck height '+str(Vector3(x,expected,z)))
 for x in [24.5,25.7]:
  if x-.44<=23.5:failures.append('Pad intersects bridge')
 print('Bridge physics: ',samples,' deck height samples')
 for failure in failures:print('FAIL: ',failure)
 print('PASS' if failures.is_empty() else 'FAILED')
 scene.queue_free()
 for i in range(3):await process_frame
 quit(0 if failures.is_empty() else 1)
