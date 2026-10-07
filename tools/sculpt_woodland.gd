extends SceneTree
# One-time editor authoring operation. Builds never invoke this script.
func _initialize():call_deferred("run")
func tri(st:SurfaceTool,a:Vector3,b:Vector3,c:Vector3):
 for v in [a,b,c]:st.add_vertex(v)
func mesh_from(st:SurfaceTool,material:Material):
 st.generate_normals()
 var mesh=st.commit()
 mesh.surface_set_material(0,material)
 return mesh
func owned(parent:Node,node:Node,scene:Node):
 parent.add_child(node);node.owner=scene
func run():
 var path="res://EXTERNAL/Touma/SafariZone/Woodland/WoodlandPassage.tscn"
 var scene=load(path).instantiate()
 var group=scene.get_node("Escarpments")
 for old in group.get_children():
  if not is_instance_valid(old):continue
  if not old is CSGPolygon3D or old.name.ends_with("Turf"):continue
  var outline=old.polygon
  var height=old.depth
  var points=PackedVector2Array()
  for i in outline.size():
   var a=outline[i];var b=outline[(i+1)%outline.size()]
   var count=int(ceil(a.distance_to(b)/6.0))
   for j in count:points.append(a.lerp(b,float(j)/count))
  var center=Vector2.ZERO
  for p in points:center+=p
  center/=points.size()
  var tops=[];var bases=[];var shoulders=[]
  for i in points.size():
   var p=points[i]
   var noise=sin(p.x*.36+p.y*.17)+.55*cos(p.x*.73-p.y*.29)
   var h=height+noise*(1.45 if height>5 else .22)
   var top=center+(p-center)*.95
   tops.append(Vector3(top.x,h,top.y))
   bases.append(Vector3(p.x,0,p.y))
   var bulge=center+(p-center)*(1.01+.016*sin(i*2.3))
   shoulders.append(Vector3(bulge.x,h*.48,bulge.y))
  var sides=SurfaceTool.new();sides.begin(Mesh.PRIMITIVE_TRIANGLES)
  for i in points.size():
   var j=(i+1)%points.size()
   var shade=.83+.15*sin(i*1.8)
   sides.set_color(Color(shade,shade,shade,1))
   tri(sides,bases[i],shoulders[j],bases[j]);tri(sides,bases[i],shoulders[i],shoulders[j])
   tri(sides,shoulders[i],tops[j],shoulders[j]);tri(sides,shoulders[i],tops[i],tops[j])
  var rock=old.material.duplicate();rock.cull_mode=BaseMaterial3D.CULL_DISABLED;rock.vertex_color_use_as_albedo=true
  var body_mesh=mesh_from(sides,rock)
  var top=SurfaceTool.new();top.begin(Mesh.PRIMITIVE_TRIANGLES)
  var indices=Geometry2D.triangulate_polygon(points)
  for i in range(0,indices.size(),3):tri(top,tops[indices[i]],tops[indices[i+2]],tops[indices[i+1]])
  var turf=group.get_node(str(old.name)+"Turf").material.duplicate();turf.cull_mode=BaseMaterial3D.CULL_DISABLED
  var top_mesh=mesh_from(top,turf)
  var land=Node3D.new();land.name=str(old.name)+"Sculpted"
  land.set_meta("polygon",outline)
  owned(group,land,scene)
  var face=MeshInstance3D.new();face.name="RockFaces";face.mesh=body_mesh;owned(land,face,scene)
  var cap=MeshInstance3D.new();cap.name="PlantedTop";cap.mesh=top_mesh;owned(land,cap,scene)
  var body=StaticBody3D.new();body.name="Collision";body.collision_layer=11;body.collision_mask=0;owned(land,body,scene)
  var collision=CollisionShape3D.new();collision.shape=body_mesh.create_trimesh_shape();owned(body,collision,scene)
  var top_collision=CollisionShape3D.new();top_collision.name="TopCollision";top_collision.shape=top_mesh.create_trimesh_shape();owned(body,top_collision,scene)
  group.get_node(str(old.name)+"Turf").free();old.free()
 for n in group.find_children("*","CollisionShape3D",true,false):
  if n.shape is ConcavePolygonShape3D:n.shape.backface_collision=true
 var terrain=group.duplicate()
 root.add_child(terrain)
 for i in range(12):await physics_frame
 # Extra middle-ground tree clusters frame the rock shelves, away from the paths.
 var extra_positions=[Vector2(-18,-10),Vector2(-8,-17),Vector2(5,-17),Vector2(17,-21),Vector2(30,-12),Vector2(38,-19)]
 for i in extra_positions.size():
  var name="Tree"+str(22+i)
  if scene.get_node("Planting").has_node(name):continue
  var tree=load("res://Scenes/FunctionalObjects/TreeBFunctional.tscn" if i%2 else "res://Scenes/FunctionalObjects/TreeCFunctional.tscn").instantiate()
  tree.name=name;tree.position=Vector3(extra_positions[i].x,0,extra_positions[i].y);tree.scale=Vector3(1.9,1.9,1.9)
  owned(scene.get_node("Planting"),tree,scene)
 # Reground terrace planting after sculpting the upper surfaces.
 for n in scene.get_node("Planting").get_children():
  if not n.name.begins_with("Tree") and not n.name.begins_with("SkylineTree"):continue
  var query=PhysicsRayQueryParameters3D.create(Vector3(n.position.x,40,n.position.z),Vector3(n.position.x,-1,n.position.z),11)
  var hit=root.get_world_3d().direct_space_state.intersect_ray(query)
  n.position.y=hit.position.y+.06 if hit else 0.0
 if scene.has_node("CliffPlanting"):scene.get_node("CliffPlanting").free()
 var planting=Node3D.new();planting.name="CliffPlanting";owned(scene,planting,scene)
 var ivy=load("res://Art/Decorations/Foliage/IvyB.png")
 for p in [Vector2(-30,6),Vector2(-21,6),Vector2(-8,8),Vector2(4,8),Vector2(21,7),Vector2(34,6),Vector2(-20,2.2),Vector2(34,2.6)]:
  var query=PhysicsRayQueryParameters3D.create(Vector3(p.x,p.y,25),Vector3(p.x,p.y,-42),11)
  var hit=root.get_world_3d().direct_space_state.intersect_ray(query)
  if not hit:continue
  var vine=Sprite3D.new();vine.texture=ivy;vine.modulate=Color(.35,.63,.39,1);vine.pixel_size=.0035;vine.alpha_cut=SpriteBase3D.ALPHA_CUT_DISCARD;vine.no_depth_test=false
  vine.position=hit.position+hit.normal*.045
  owned(planting,vine,scene)
  vine.basis=Basis.looking_at(-hit.normal,Vector3.UP)
 for p in [Vector2(-31,-13),Vector2(-24,-13),Vector2(-18,-16),Vector2(-16,-10),Vector2(-21,-7),Vector2(-27,-8),Vector2(31,-11),Vector2(35,-12),Vector2(38,-16),Vector2(30,-17),Vector2(-14,-5),Vector2(-16,-5)]:
  var query=PhysicsRayQueryParameters3D.create(Vector3(p.x,40,p.y),Vector3(p.x,-1,p.y),11)
  var hit=root.get_world_3d().direct_space_state.intersect_ray(query)
  if not hit:continue
  var grass=load("res://Scenes/Decorations/GreenGrassB.tscn").instantiate()
  grass.position=hit.position+Vector3(0,.12,0);grass.scale=Vector3(2,2,2)
  owned(planting,grass,scene)
 terrain.free()
 var packed=PackedScene.new();packed.pack(scene)
 var error=ResourceSaver.save(packed,path)
 scene.free()
 print("Sculpted cliff scene saved: ",error)
 quit(error)
