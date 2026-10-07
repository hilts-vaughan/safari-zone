---
name: flock-mod-test
description: Validate Flock Around mods in the installed game with disposable saves and isolated X11 input, and diagnose loading, spawn, or perch errors.
---

Work from the repository root. Read [validation notes](../../docs/VALIDATION.md) for established results and limitations. Run `tools/validate_mod.py` against the current game pack before runtime checks.

Prefer the checked-in `tools/regression_mod.py --game-dir /path/to/FlockAround --output test-results/new-run --roster all` over recreating shell procedures. See [workflow instructions](../../docs/WORKFLOWS.md). It owns isolation, cleanup, log assertions, spawn IDs, and evidence. Strict error handling is the default; the known startup allowance must be explicit and disclosed. Use `python3 -m unittest discover -s tests -v` when changing workflow scripts.

## Isolate

Use fresh temporary `XDG_DATA_HOME` and `XDG_CONFIG_HOME` directories. Copy the mod to `<XDG_DATA_HOME>/SecretPlan/FlockAround/Mods/Touma/SafariZone`. Inspect the current settings schema before preparing temporary settings; change only the isolated copy. Disable telemetry and enable console/mod consent there. Preserve the real save and Steam settings.

Use a disposable X11 display such as `xvfb-run`. `tools/ui_driver.py` uses XTest and rejects common personal desktop displays. Keep input automation on the selected disposable display. Its text helper handles lowercase commands, not arbitrary text requiring Shift.

The internal `--localhost` path auto-hosts the level selected in temporary `preferred_lobby_settings.level` and binds UDP 1027. Avoid concurrent hosts. `SteamAppId=3618030` may be needed to prevent Steam relaunch. Capture logs and track the process PID; clean up only this test's processes. Verify executable and temporary-save environment before terminating a stale host.

## Exercise and report

- Check config loading, bird population, and biome assignment in logs.
- Console commands `spawn <species>`, `list birds`, and `spectate <id>` allow roster inspection. Read IDs from results. Use `hooh` for Ho-Oh because species-name matching strips hyphens.
- Inspect sprites, movement, and guidebook labels. Seeing an index entry does not prove photo scoring: that requires capture and development checks.
- After perch changes, allow movement and inspect for branch lookup errors. The existing workaround avoids Tree preferences and uses stock flat canopy hangouts with the Rock descriptor.

Internal localhost startup previously raised `GameCore.FinishLoadScene` null-reference errors and left a loading overlay. Console `loadingscrim fullclear` cleared that overlay for testing. Disclose this if it occurs; clearing it does not establish normal UI startup. Do not prescribe this command for normal installation.

Record versions, actual assertions, screenshots, and unresolved errors in `docs/VALIDATION.md`. Distinguish static validation, isolated runtime, normal UI startup, scoring, and multiplayer. Do not claim unexercised features passed. Repeat broad checks only when changes or unresolved concerns justify them.
