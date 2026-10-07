extends SceneTree
func _initialize():
 call_deferred("preview")
func preview():
 var world = load("res://Levels/SafariZone.tscn").instantiate()
 root.add_child(world)
 var env = WorldEnvironment.new()
 env.environment=Environment.new()
 env.environment.background_mode=Environment.BG_COLOR
 env.environment.background_color=Color("bfe4ea")
 env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
 env.environment.ambient_light_color=Color("fff3df")
 env.environment.ambient_light_energy=.7
 world.add_child(env)
 var light=DirectionalLight3D.new()
 light.rotation_degrees=Vector3(-55,-25,0)
 light.light_energy=1.2
 world.add_child(light)
 var cam=Camera3D.new()
 world.add_child(cam)
 cam.position=Vector3(125,102,136)
 cam.look_at(Vector3(0,0,0))
 cam.fov=48
 cam.current=true
 await create_timer(2).timeout
 await RenderingServer.frame_post_draw
 var output=OS.get_cmdline_user_args()[0]
 var err=root.get_texture().get_image().save_png(output)
 print("Preview capture: ",output," result: ",err)
 quit(err)
