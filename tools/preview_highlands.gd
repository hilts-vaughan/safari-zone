extends SceneTree
func _initialize():call_deferred('run')
func clean(n):
 for c in n.get_children():
  var s=c.get_script()
  if s!=null and str(s.resource_path).ends_with('FreeOnReady.cs'):
   n.remove_child(c);c.free()
  else:clean(c)
 if n is Label3D:n.visible=false
 n.set_script(null)
func run():
 var scene=load('res://Levels/SafariZone.tscn').instantiate();clean(scene);root.add_child(scene)
 var camera=Camera3D.new();root.add_child(camera);camera.current=true;camera.fov=75
 var views=[['highlands-overview',Vector3(17,13,-5),Vector3(72,7,-77)],['highlands-approach',Vector3(51,2.1,-40),Vector3(62,8,-83)],['highlands-summit',Vector3(74,18,-87),Vector3(86,1,-28)]]
 var directory=OS.get_cmdline_user_args()[0];DirAccess.make_dir_recursive_absolute(directory)
 for view in views:
  camera.position=view[1];camera.look_at(view[2])
  for i in range(30):await process_frame
  await RenderingServer.frame_post_draw
  root.get_texture().get_image().save_png(directory+'/'+view[0]+'.png');print('Saved ',view[0])
 scene.free();camera.free();quit()
