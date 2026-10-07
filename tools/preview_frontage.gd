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
  ["arrival-west-gateway",Vector3(-101,2.1,90),Vector3(-94,2,74)],
  ["arrival-west-grass",Vector3(-92,2.2,97),Vector3(-95,3,83)],
  ["arrival-east-gateway",Vector3(-49,2.1,88),Vector3(-45,2,72)],
  ["frontage-front",Vector3(-82,3.5,100),Vector3(-55,7,82)],
  ["frontage-reverse",Vector3(-22,5,67),Vector3(-65,7,89)],
  ["frontage-tower-view",Vector3(-40,16.6,84.8),Vector3(-80,2,32)]
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
