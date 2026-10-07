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
 Engine.time_scale=4
 for i in range(12):await physics_frame
 var routes=[[Vector3(42,0,-56),Vector3(42,4,-68),Vector3(58,9,-68),Vector3(58,9,-77),Vector3(74,16,-77),Vector3(74,16,-87)], [Vector3(58,9,-77),Vector3(58,9,-82),Vector3(88,9,-82),Vector3(88,9,-76),Vector3(106,7,-76),Vector3(106,7,-87)], [Vector3(42,4,-68),Vector3(42,4,-76)]]
 var failures=[];var completed=0
 for route in routes:
  for reverse in [false,true]:
   var points=route.duplicate()
   if reverse:points.reverse()
   var body=CharacterBody3D.new();body.collision_layer=0;body.collision_mask=3;body.floor_snap_length=0.6;body.floor_max_angle=deg_to_rad(45);body.safe_margin=0.002
   var shape=CollisionShape3D.new();var cap=CapsuleShape3D.new();cap.radius=0.35;cap.height=1.8;shape.shape=cap;shape.position.y=0.9;body.add_child(shape);root.add_child(body);body.position=points[0]+Vector3(0,0.04,0)
   var good=true
   for target in points.slice(1):
    var reached=false
    for step in range(800):
     await physics_frame
     var d=Vector3(target.x-body.position.x,0,target.z-body.position.z)
     if d.length()<0.18:
      reached=true;break
     var direction=d.normalized();body.velocity.x=direction.x*min(6.0,d.length()*8);body.velocity.z=direction.z*min(6.0,d.length()*8)
     body.velocity.y=-1.0 if body.is_on_floor() else body.velocity.y-18*4/60.0
     body.move_and_slide()
     if body.position.y<-1:break
    if not reached or abs(body.position.y-target.y)>0.25:
     failures.append('Target '+str(target)+' reverse '+str(reverse)+' stopped '+str(body.position));good=false;break
   if good:completed+=1
   body.free()
 print('Highlands moving capsule: ',completed,'/6 ascending/descending routes; ',failures.size(),' failures')
 for f in failures:print('FAIL: ',f)
 scene.free();quit(0 if failures.is_empty() else 1)
