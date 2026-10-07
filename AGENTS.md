# Safari Zone mod workspace

Read `docs/MODDING_GUIDE.md` before changing the mod. The project uses Flock Around's native config-and-scene mod system, not a code injection framework.

Reusable project skills are stored in `skills/` because this environment's `.agents` directory is read-only. Read the relevant skill for these tasks:

- `skills/flock-mod-build/SKILL.md`: authoring, source research, export, validation, and packaging.
- `skills/flock-mod-test/SKILL.md`: isolated runtime checks and diagnosis.
- `skills/flock-mod-install/SKILL.md`: local installation and updates.

- `data/roster.csv` is the species source of truth. User-authorized scope now includes the saved Gen 4–6 Imagegen birds and winged insects. Legacy species are retired from the release; preserve their source art for provenance.
- `tools/build_mod.py` generates configs, the guidebook map, and the Godot scene. Character artwork is saved under `assets/birds/`; `tools/art.py` only copies it into the release. Use Imagegen for new character art, as requested by the user. Do not replace it with procedural character drawings.
- Preserve original Imagegen outputs and exact requests under `assets/imagegen/<species>/`. `tools/pack_imagegen.py` crops and uniformly registers reviewed component boards into three-head/five-body strips, using attachment points in `layout.json`. It must not redraw anatomy. Review all five assembled poses with `tools/preview_art.py` before packaging. Generation rejections stay recorded; never label legacy fallback sprites as new Imagegen art.
- Keep `Touma/SafariZone` and stable IDs intact across updates. Validate collisions against the installed pack.
- Use the official editor at `editor/SceneEditor` with Godot 4.6.2 .NET. Custom external resources must be namespaced beneath `res://EXTERNAL/` and exported with the official exporter.
- Native branch perches reported lookup failures in local testing. The current mod uses stock flat canopy hangouts with the Rock descriptor, plus bush, ground, and player perches. Preserve this workaround unless a new test demonstrates a reliable replacement.
- Validate with `python3 tools/validate_mod.py /path/to/FlockAround.pck`, then package with `python3 tools/package_mod.py`.
- Prefer the checked-in build, regression, and deployment entrypoints documented in `docs/WORKFLOWS.md`. Workflow script changes should pass `python3 -m unittest discover -s tests -v`. Runtime reports must fail on unexpected errors, including errors emitted during shutdown; the known localhost startup allowance is explicit and remains reported.
- Runtime tests must use a disposable `XDG_DATA_HOME` and save directory. The internal `--localhost` option binds UDP port 1027; avoid concurrent local hosts and terminate test processes afterward. Its startup may leave a loading overlay, which the test console clears using `loadingscrim fullclear`. This is not required by normal installation.
- Never include installed game packs, decompiled code, personal save files, test settings, or the editor cache in the mod archive.
