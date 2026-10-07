---
name: flock-mod-build
description: Create or update native Flock Around bird and map mods in this workspace, then export, validate, and package them.
---

Work from the repository root (two directories above this skill). Read [the modding guide](../../docs/MODDING_GUIDE.md) for schemas and tutorial evidence, and root `AGENTS.md` for project conventions.

Use `tools/build_release.py --game-pack /path/to/FlockAround.pck --godot /path/to/godot` for the complete build/export/validate/package sequence. Read [workflow instructions](../../docs/WORKFLOWS.md) for dependencies and reproducibility limits.

## Author and research

- Edit `data/roster.csv`, `tools/build_mod.py`, and saved artwork under `assets/birds/`; `dist/` contains generated outputs. Use Imagegen for character art. `tools/art.py` copies saved files; builds must never generate new character designs. Preserve namespace and existing config/localization IDs across updates.
- Save Imagegen outputs and exact prompts under `assets/imagegen/<species>/`. Author crop rectangles and attachment points in its `layout.json`, run `python3 tools/pack_imagegen.py <species>`, then review `python3 tools/preview_art.py`. Packing may crop, resample and align pixels, but must not draw substitute anatomy. Keep recorded failures and legacy fallbacks explicit in `assets/birds/provenance.json`.
- Check native schemas and enums against the installed game pack rather than guessing. `tools/read_pck.py` lists matching paths; its `Pack.read()` reads entries without changing the pack. Official samples are under `editor/Samples`.
- Tutorial transcripts, video metadata, and the Steam announcement are cached under `docs/sources`. Consult those before fetching again. Record source URLs, versions, and distinctions between documented behavior and observed workarounds in the guide.
- New birds need the native three-frame head strip, five-frame body strip, mockup, calls, localization, and biome references. Follow the generator's frame order and dimensions unless current official evidence supports a change.
- Custom external map resources belong beneath `res://EXTERNAL/<author>/<mod>/` and need official export. Do not bundle vanilla game resources.
- Safari Zone currently uses flat canopy/rock hangouts instead of native branch perches because of observed lookup failures. Changes to this arrangement need a runtime regression.

## Build and deliver

Locate the installed pack using the current user's `$HOME`, rather than a hardcoded username. On Linux, check `$HOME/.local/share/Steam/steamapps/common/FlockAround/FlockAround.pck` and `$HOME/.steam/steam/steamapps/common/FlockAround/FlockAround.pck`. If absent, inspect Steam's `steamapps/libraryfolders.vdf` for additional libraries, or use Steam's Browse local files option. Verify the pack exists before passing its absolute path to the build tools.

```sh
python3 tools/build_mod.py /path/to/FlockAround.pck
python3 tools/validate_mod.py /path/to/FlockAround.pck
```

Export the final generated scene with Godot 4.6.2 .NET and the patched official editor. Build the editor assembly first; its name must match `project.godot`. Set `FLOCK_MOD_OUTPUT` to the absolute `dist/Touma/SafariZone` path, then invoke:

```sh
/path/to/godot --headless --path editor/SceneEditor -- --export-scene res://Levels/SafariZone.tscn /path/to/FlockAround.pck
```

If the required .NET runtime is unavailable, check installed runtimes; `DOTNET_ROLL_FORWARD=Major` previously allowed the editor to use a newer installed runtime. Temporary binaries and caches may disappear: locate dependencies rather than assuming `/tmp` persists.

Validate again after export, then run `python3 tools/package_mod.py`. A scene with only vanilla references and embedded geometry legitimately needs no custom PCK or UID sidecar. Exclude game packs, saves, caches, and research transcripts from the mod ZIP. Update `docs/VALIDATION.md` with checks actually performed. Building alone does not authorize installation or publishing.
