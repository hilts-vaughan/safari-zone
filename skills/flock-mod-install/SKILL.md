---
name: flock-mod-install
description: Install or update a built Flock Around mod in the user's local Mods directory and verify the installed payload.
---

Use when local installation is requested. Work from the repository root and consult [installation instructions](../../README.md). Local installation does not authorize Workshop publishing or save changes.

Prefer `python3 tools/deploy_mod.py --mods-dir /path/to/save/Mods` to verify and inspect, then add `--apply` for authorized installation. The script verifies the manifest, stages the payload, backs up updates outside Mods, removes stale active files, and rolls back installation exceptions. Read [workflow instructions](../../docs/WORKFLOWS.md) for single-writer and interrupted-process limits. Avoid reimplementing deployment with ad hoc copy/delete commands.

Locate save data through the game's Open Save Data option or existing filesystem. On Linux, check `${XDG_DATA_HOME:-$HOME/.local/share}/SecretPlan/FlockAround` using the current user's environment; verify this is the real save directory, not a disposable test directory. If it is absent or ambiguous, use Open Save Data to confirm the location. Pass its `Mods` directory to `--mods-dir`; the mod destination beneath it is `Touma/SafariZone`, a stable namespace independent of the OS username. Do not confuse save data with the Steam game directory.

Confirm `dist/Touma/SafariZone` is the current validated build and inspect the destination. For a first install, copy the complete author/mod hierarchy. For updates, preserve a backup outside Mods to avoid duplicate config loading, then replace only this mod's directory so obsolete files do not survive. Preserve unrelated mods. Follow the environment's escalation mechanism for writes outside the workspace.

Verify the installed directory matches the source with `diff -qr` or file hashes, and confirm `Mods/Touma/SafariZone/Level_SafariZone.json` exists. Report destination and result. For first activation, explain Steam launch option `-- --enablemods`, mod consent/restart, enabling local mods in Manage Mods, and selecting Safari Zone when creating a game. Do not launch or alter Steam configuration unless within the user's requested scope.

Retain user-confirmed normal startup separately from localhost automation results. Successful installation does not establish scoring, multiplayer, or Workshop compatibility.
