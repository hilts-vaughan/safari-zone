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
  ["fountain-approach",Vector3(-73,2.1,-26),Vector3(-74,1,-17)],
  ["fountain-side",Vector3(-87,2.1,-19),Vector3(-74,1,-18)],
  ["fountain-overview",Vector3(-79,12,-25),Vector3(-75,0,-18)]
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
