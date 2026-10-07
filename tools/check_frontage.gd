extends SceneTree
func _initialize():call_deferred("run")
func strip_scripts(node):
 for child in node.get_children():strip_scripts(child)
 node.set_script(null)
func run():
 var packed=load("res://Levels/SafariZone.tscn")
 if packed==null:quit(1);return
 var scene=packed.instantiate()
 strip_scripts(scene);root.add_child(scene)
 for i in range(12):await physics_frame
 var cases=JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
 var failures=[];var space=root.get_world_3d().direct_space_state
 var capsule=CapsuleShape3D.new();capsule.radius=.32;capsule.height=1.6
 for p in cases.walk:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],p[2]+.35,p[1]),Vector3(p[0],p[2]-.35,p[1]),11))
  if not hit:failures.append("Missing stair/deck "+str(p));continue
  if abs(hit.position.y-p[2])>.16:failures.append("Wrong stair height "+str(p));continue
  var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.collision_mask=11
  q.transform=Transform3D(Basis(),Vector3(p[0],hit.position.y+.92,p[1]))
  var hits=space.intersect_shape(q,4)
  if not hits.is_empty():failures.append("Blocked stair/deck "+str(p)+": "+str(hits[0].collider.get_path()))
 for p in cases.paths:
  var q=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.collision_mask=11
  q.transform=Transform3D(Basis(),Vector3(p[0],1.08,p[1]))
  var hits=space.intersect_shape(q,4)
  if not hits.is_empty():failures.append("Blocked entrance path "+str(p)+": "+str(hits[0].collider.get_path()))
 # Fence barriers must physically join the gateways and block walking around them.
 var fence_samples=0
 for line in cases.fences:
  var a=Vector2(line[0][0],line[0][1]);var b=Vector2(line[1][0],line[1][1]);var normal=(b-a).normalized().orthogonal()
  for i in range(1,10):
   var p=a.lerp(b,i/10.0);var left=p+normal*.8;var right=p-normal*.8
   var query=PhysicsRayQueryParameters3D.create(Vector3(left.x,.6,left.y),Vector3(right.x,.6,right.y),11)
   var hit=space.intersect_ray(query);var ignored:Array[RID]=[]
   # At the cliff connections, inspect the fence behind overlapping native rock.
   for repeat in range(6):
    if not hit or str(hit.collider.get_path()).contains('ArrivalFence'):break
    ignored.append(hit.rid);query.exclude=ignored;hit=space.intersect_ray(query)
   if not hit or not str(hit.collider.get_path()).contains('ArrivalFence'):failures.append('Missing fence barrier at '+str(p)+': '+(str(hit.collider.get_path()) if hit else 'no collision'))
   fence_samples+=1
 for p in cases.perches:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p[0],p[2]+.3,p[1]),Vector3(p[0],p[2]-.2,p[1]),11))
  if not hit or abs(hit.position.y-(p[2]+.08))>.05:failures.append('Unsupported bird post at '+str(p))
 print('Landscape physics: ',fence_samples,' fence barrier samples; ',cases.perches.size(),' supported bird posts')
 # Walk in parallel on both sides and the center of the usable stair width.
 var walkers=[]
 for radius in [1.65,2.1,2.55]:
  var walker=CharacterBody3D.new();walker.collision_layer=0;walker.collision_mask=11;walker.floor_snap_length=.3
  var shape=CollisionShape3D.new();var moving_capsule=CapsuleShape3D.new();moving_capsule.radius=.4;moving_capsule.height=1.8
  shape.shape=moving_capsule;shape.position.y=.9;walker.add_child(shape);root.add_child(walker)
  walker.position=Vector3(-35.9,15.05 if cases.descending else .03,89)
  var route=[Vector3(-40+radius,15 if cases.descending else 0,89)]
  for i in (range(1199,-1,-1) if cases.descending else range(1,1201)):
   var t=i*TAU*5/1200;route.append(Vector3(-40+radius*cos(t),15.0*i/1200,89+radius*sin(t)))
  route.append(Vector3(-35.9,0 if cases.descending else 15,89))
  walkers.append({'body':walker,'route':route,'target':0,'radius':radius,'last_progress':0})
 var ticks=0
 while ticks<4200:
  await physics_frame
  var finished=true
  for state in walkers:
   var walker=state.body
   if state.target>=state.route.size():continue
   finished=false
   var offset=state.route[state.target]-walker.position;offset.y=0
   # Follow the usable width with a short forward lookahead.
   if offset.length()<.12:
    state.target+=1;state.last_progress=ticks;continue
   var direction=offset.normalized();walker.velocity.x=direction.x*3;walker.velocity.z=direction.z*3
   walker.velocity.y=0 if walker.is_on_floor() else walker.velocity.y-15.0/60
   walker.move_and_slide()
  ticks+=1
  if finished:break
  if walkers.any(func(state):return state.target<state.route.size() and ticks-state.last_progress>300):break
 for state in walkers:
  if state.target<state.route.size() or abs(state.body.position.y-(0 if cases.descending else 15))>.25:
   failures.append('Full spiral climb failed at radius '+str(state.radius)+' target '+str(state.target)+': '+str(state.body.position))
   print('Goal: ',state.route[state.target],' velocity ',state.body.velocity,' floor ',state.body.is_on_floor(),' wall ',state.body.is_on_wall())
   for j in range(state.body.get_slide_collision_count()):
    var contact=state.body.get_slide_collision(j);print('Contact: ',contact.get_collider().get_path(),' normal ',contact.get_normal(),' position ',contact.get_position())
  else:print('PASS: full-width climb radius ',state.radius,' descent reached ground at ' if cases.descending else ' ascent reached deck at ',state.body.position)
  state.body.free()
 print("Frontage physics: ",cases.walk.size()," spiral/deck samples; ",cases.paths.size()," entrance route samples")
 for failure in failures:print("FAIL: ",failure)
 scene.free();scene=null;packed=null
 for i in range(12):await process_frame
 print("PASS" if failures.is_empty() else "FAILED");quit(0 if failures.is_empty() else 1)
