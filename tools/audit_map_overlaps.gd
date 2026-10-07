extends SceneTree
func _initialize():call_deferred('run')
func clean(n):
 for c in n.get_children():
  var s=c.get_script()
  if s!=null and str(s.resource_path).ends_with('FreeOnReady.cs'):
   n.remove_child(c);c.free()
  else:clean(c)
 n.set_script(null)
func descendants(n,out):
 for c in n.get_children():
  if c is CollisionObject3D:out.append(c.get_rid())
  descendants(c,out)
var tree_rids=[]
func gather(n):
 if n is Node3D and str(n.scene_file_path).contains("Tree") and str(n.scene_file_path).contains("Functional") and not str(n.name).contains("Rustle"):
  descendants(n,tree_rids)
 for c in n.get_children():gather(c)
func scan(n,out):
 if n is Node3D:
  var source=str(n.scene_file_path)
  if not str(n.name).contains('Rustle') and (source.ends_with('RockHangout.tscn') or (source.contains('Tree') and source.contains('Functional'))):
   var p=n.global_position
   var exclude=tree_rids.duplicate();descendants(n,exclude)
   var q=PhysicsRayQueryParameters3D.create(Vector3(p.x,40,p.z),Vector3(p.x,-2,p.z),11,exclude)
   var hit=root.get_world_3d().direct_space_state.intersect_ray(q)
   var row={'name':str(n.get_path()),'source':source,'position':[p.x,p.y,p.z],'scale':[n.global_basis.get_scale().x,n.global_basis.get_scale().y,n.global_basis.get_scale().z]}
   if hit:
    row['surface_y']=hit.position.y;row['collider']=str(hit.collider.get_path())
   if str(n.name).begins_with('CliffShelfLanding'):
    var samples=[]
    for delta in [Vector2(-1.55,-.85),Vector2(-1.55,.85),Vector2(1.55,-.85),Vector2(1.55,.85)]:
     var ray=PhysicsRayQueryParameters3D.create(Vector3(p.x+delta.x,40,p.z+delta.y),Vector3(p.x+delta.x,-2,p.z+delta.y),11,exclude)
     var h=root.get_world_3d().direct_space_state.intersect_ray(ray)
     if h:samples.append({'x':p.x+delta.x,'z':p.z+delta.y,'surface_y':h.position.y,'collider':str(h.collider.get_path())})
    row['shelf_corners']=samples
   out.append(row)
 for c in n.get_children():scan(c,out)
func run():
 var scene=load('res://Levels/SafariZone.tscn').instantiate();clean(scene);root.add_child(scene)
 for i in range(10):await physics_frame
 gather(scene)
 var out=[];scan(scene,out)
 var output=OS.get_cmdline_user_args()[0] if OS.get_cmdline_user_args().size()>0 else '/tmp/map-overlap-observations.json'
 var f=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(out,'  '));f.close()
 scene.queue_free()
 for i in range(3):await process_frame
 quit()
