extends SceneTree

func _initialize():call_deferred("run")

func strip_scripts(node):
 for child in node.get_children():
  if child is Label3D:child.visible=false
  var script=child.get_script()
  if script!=null and str(script.resource_path).ends_with("FreeOnReady.cs"):
   node.remove_child(child);child.free()
  else:strip_scripts(child)
 node.set_script(null)

func run():
 var packed=load("res://Levels/SafariZone.tscn")
 if packed==null:quit(1);return
 var scene=packed.instantiate();strip_scripts(scene);root.add_child(scene)
 var camera=Camera3D.new();root.add_child(camera);camera.current=true;camera.fov=65
 var views=[
  ["grasslands-center-transition",Vector3(-95,2.2,77),Vector3(-96,2,45)],
  ["grasslands-tree-lane",Vector3(-91,2.2,51),Vector3(-91,2,18)],
  ["grasslands-overview",Vector3(-102,28,100),Vector3(-82,0,31)],
  ["grasslands-ground",Vector3(-91,2.4,60),Vector3(-86,1.3,29)],
  ["grasslands-observation-deck",Vector3(-127,5.2,30),Vector3(-75,1.2,34)]
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
