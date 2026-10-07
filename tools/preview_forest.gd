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
  ["forest-gate-approach",Vector3(-110,2.1,3),Vector3(-111,2,-3)],
  ["forest-gate-forest-side",Vector3(-104,2.1,-17),Vector3(-111,2,-3)],
  ["grasslands-gate-approach",Vector3(-111,2.1,19),Vector3(-111,2,-3)],
  ["natural-forest-edge",Vector3(-65,2.1,16),Vector3(-35,3,-7)],
  ["forest-boundary-overview",Vector3(-68,22,23),Vector3(-70,1,-8)]
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
