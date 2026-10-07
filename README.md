# Safari Zone for Flock Around

A birdwatching reserve with some Pokemon baked in with four habitat zones. This project is intended to be a tool to learn Godot and play with modern LLMs and exercise their capabilities. As such, I will not be publishing on Steam for two reasons:

- I do not believe this to be a product but instead a sandbox for me to play and learn
- I don't want generative art to steal the luster from what the community may come up with

The reserve uses Flock Around's native mod system and base-game assets. Wetlands Rest has working shop and photo counters, free passage, and no indoor object landing areas. The forest checkpoint requires 10 stars. This may seem like a strange choice but it's mostly just to test how the system works.

## Install

1. Extract `SafariZone.zip` into the game's **Mods** directory. The resulting path must be `Mods/Touma/SafariZone/Level_SafariZone.json`.
2. In Steam, set Flock Around's launch options to `-- --enablemods`.
3. Launch the game, accept its modding prompt, and restart if requested. Enable the local mods directory in **Manage Mods**.
4. Create a game and select **Safari Zone**.

## Automated ZIP downloads

Every push runs the **Package Safari Zone** GitHub Action, checks the repository's
regression tests, and packages the exported payload in `dist/Touma/SafariZone`.
Open the [Actions page](https://github.com/hilts-vaughan/safari-zone/actions),
select a successful run, and download its `SafariZone-<commit SHA>` artifact.
Extract that artifact download to get the installable `SafariZone.zip`.
Artifacts are retained for 30 days. The workflow can also be run manually.

This packages the checked-in export; it does not regenerate the mod from source.
After changing source assets or scene-generation code, run the local release
builder and commit the updated `dist/Touma/SafariZone` files before pushing.
Full generation and scene export require the installed game pack and Godot .NET.

## Local rebuild

There are tools provided to help with basic tasks:

Python 3 and Pillow are required. Supply the installed game's pack:

```sh
python3 tools/build_mod.py /path/to/FlockAround.pck
python3 tools/validate_mod.py /path/to/FlockAround.pck
```

For editing/exporting the scene, open `editor/SceneEditor/project.godot` with **Godot 4.6.2 .NET**, build, and use its export tool. The generated scene is `res://Levels/SafariZone.tscn`. Custom headless export support was added to the official exporter; set `FLOCK_MOD_OUTPUT` to an absolute output directory and invoke the project with user arguments `--export-scene res://Levels/SafariZone.tscn /path/to/FlockAround.pck`. The `.csproj` explicitly sets the assembly name to match `project.godot`.

You can edit the project manually but some of the tools included have been used to place things automatically.
