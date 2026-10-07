extends SceneTree
func _initialize():call_deferred('run')
func clean(n):
 for c in n.get_children():
  var s=c.get_script()
  if s!=null and str(s.resource_path).ends_with('FreeOnReady.cs'):
   n.remove_child(c);c.free()
  else:clean(c)
 n.set_script(null)
func collect(n,out):
 if n is Node3D and str(n.scene_file_path).ends_with('RockHangout.tscn') and (str(n.get_path()).contains('/CliffFountainGarden/') or str(n.name).begins_with('Fountain') or str(n.name).begins_with('UpperBowlLanding')):out.append(n)
 for c in n.get_children():collect(c,out)
func foliage(n,out):
 if n is CollisionObject3D and str(n.name)=='BlockLineOfSight':out.append(n.get_rid())
 for c in n.get_children():foliage(c,out)
func run():
 var scene=load('res://Levels/SafariZone.tscn').instantiate();clean(scene);root.add_child(scene)
 for i in range(10):await physics_frame
 var perches=[];collect(scene,perches)
 var leaves=[];foliage(scene,leaves)
 var failures=[];var count=0
 for perch in perches:
  for offset in [Vector3.ZERO,Vector3(-.44,0,-.44),Vector3(-.44,0,.44),Vector3(.44,0,-.44),Vector3(.44,0,.44)]:
   var p=perch.global_transform*offset
   var hit=root.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p.x,40,p.z),p-Vector3(0,.15,0),11,leaves))
   count+=1
   if not hit or abs(hit.position.y-p.y)>.04:failures.append(str(perch.get_path())+' '+str(offset)+' '+str(hit))
 print('Fountain surface checks: ',perches.size(),' landing rectangles, ',count,' samples, ',failures.size(),' failures')
 for failure in failures:print('FAIL: ',failure)
 scene.free()
 for i in range(3):await process_frame
 quit(0 if failures.is_empty() and perches.size()==20 else 1)
