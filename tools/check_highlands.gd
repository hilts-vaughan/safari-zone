extends SceneTree
func _initialize():call_deferred('run')
func clean(n):
 for c in n.get_children():
  var s=c.get_script()
  if s!=null and str(s.resource_path).ends_with('FreeOnReady.cs'):
   n.remove_child(c);c.free()
  else:clean(c)
 n.set_script(null)
func collect(n,out,leaves):
 if n is Node3D and (str(n.name).begins_with('HighlandsLanding') or str(n.name).begins_with('HighlandsBench') and 'Landing' in str(n.name) or str(n.name).begins_with('HighlandsLegendRoost')):out.append(n)
 if n is CollisionObject3D and str(n.name)=='BlockLineOfSight':leaves.append(n.get_rid())
 for c in n.get_children():collect(c,out,leaves)
func run():
 var scene=load('res://Levels/SafariZone.tscn').instantiate();clean(scene);root.add_child(scene)
 for i in range(12):await physics_frame
 var perches=[];var leaves=[];collect(scene,perches,leaves)
 var failures=[];var count=0
 for perch in perches:
  for offset in [Vector3.ZERO,Vector3(-0.44,0,-0.44),Vector3(-0.44,0,0.44),Vector3(0.44,0,-0.44),Vector3(0.44,0,0.44)]:
   var p=perch.global_transform*offset
   var hit=root.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3(0,0.3,0),p-Vector3(0,0.2,0),11,leaves))
   count+=1
   if not hit or abs(hit.position.y-p.y)>0.045:failures.append('Perch '+str(perch.name)+' '+str(p)+' '+str(hit))
 var routes=[ [Vector3(42,0,-56),Vector3(42,4,-68),Vector3(58,9,-68),Vector3(58,9,-77),Vector3(74,16,-77),Vector3(74,16,-87)], [Vector3(58,9,-77),Vector3(58,9,-82),Vector3(88,9,-82),Vector3(88,9,-76),Vector3(106,7,-76),Vector3(106,7,-87)], [Vector3(42,4,-68),Vector3(42,4,-76)] ]
 var path_samples=0
 var cap=CapsuleShape3D.new();cap.radius=0.35;cap.height=1.8
 for route in routes:
  for i in range(route.size()-1):
   var a=route[i];var b=route[i+1];var direction=Vector3(b.x-a.x,0,b.z-a.z).normalized();var normal=Vector3(direction.z,0,-direction.x)
   for j in range(41):
    for side in [-0.8,0.0,0.8]:
     var p=a.lerp(b,j/40.0)+normal*side
     var length=Vector2(b.x-a.x,b.z-a.z).length();var trim=min(2.2,length/2-0.1)
     var ramp_t=clamp((length*j/40.0-trim)/(length-2*trim),0.0,1.0)
     p.y=lerp(a.y,b.y,ramp_t)
     var hit=root.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(p+Vector3(0,0.4,0),p-Vector3(0,0.5,0),11,leaves));path_samples+=1
     if not hit or abs(hit.position.y-p.y)>0.12:failures.append('Footing '+str(p)+' '+str(hit))
     var query=PhysicsShapeQueryParameters3D.new();query.shape=cap;query.transform=Transform3D(Basis.IDENTITY,p+Vector3(0,1.02,0));query.collision_mask=11;query.exclude=leaves
     var hits=root.get_world_3d().direct_space_state.intersect_shape(query)
     if not hits.is_empty():failures.append('Head/body clearance '+str(p)+' '+str(hits.map(func(hit):return str(hit.collider.get_path()))))
 print('Highlands support: ',perches.size(),' perches, ',count,' samples; scaffold footing/body clearance: ',path_samples,' samples; ',failures.size(),' failures')
 for f in failures.slice(0,100):print('FAIL: ',f)
 scene.free();quit(0 if failures.is_empty() else 1)
