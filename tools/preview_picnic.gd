extends SceneTree

func _initialize():call_deferred("run")

func strip_scripts(node):
 for child in node.get_children():
  var script=child.get_script()
  if script!=null and str(script.resource_path).ends_with("FreeOnReady.cs"):
   node.remove_child(child);child.free()
  else:strip_scripts(child)
 node.set_script(null)

func run():
 var packed=load("res://Levels/SafariZone.tscn")
 if packed==null:quit(1);return
 var scene=packed.instantiate();strip_scripts(scene);root.add_child(scene)
 var camera=Camera3D.new();root.add_child(camera);camera.current=true;camera.fov=75
 var views=[
  ["picnic-approach",Vector3(-53,2.1,-33),Vector3(-51,1,-17)],
  ["picnic-side",Vector3(-67,2.1,-24),Vector3(-47,1,-18)],
  ["picnic-overview",Vector3(-54,14,-30),Vector3(-50,0,-20)]
 ]
 var directory=OS.get_cmdline_user_args()[0];DirAccess.make_dir_recursive_absolute(directory)
 for view in views:
  camera.position=view[1];camera.look_at(view[2])
  for i in range(30):await process_frame
  await RenderingServer.frame_post_draw
  var path=directory+"/"+view[0]+".png"
  root.get_texture().get_image().save_png(path);print("Saved ",path)
 scene.queue_free();camera.queue_free()
 for i in range(12):await process_frame
 quit()
