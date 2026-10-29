# Test report: TLOU Outfit Changer v1.0.0

Date: 2026-10-28. Steam, The Last of Us Part I 1.1.4.0 (build 18995818),
Windows 11, NVIDIA RTX 4060. Profile that has **not** finished the story.

"Tested" means it was run and the result observed. Anything else is marked
**Not tested**.

## Offline (scan_test.exe)

| Check | tlou-i.exe | tlou-i-l.exe |
|---|---|---|
| All 6 sites located (debug flag, 2 menu checks, 3 ownership checks) | Pass | Pass |
| Sites match disassembly for this build | Pass | (no reference values) |
| Menu reads are the expected compare forms | Pass | Pass |
| Stubs: flag compare, original cmp kept, jump back after the site | Pass | Pass |
| Decision table: owned when on, game's own result when off | Pass | Pass |
| Rejects a menu check that reads another byte | Pass | Pass |
| Rejects an image with one ownership check missing | Pass | Pass |
| Fails safely when the debug menu string is missing | Pass | Pass |

## In-game (tlou-i.exe)

| Check | Result |
|---|---|
| Mod loads and installs (log: `installed: Skins menus open, every skin owned`) | Tested: pass |
| Extras > Skins opens on a never-completed profile | Tested: pass |
| Skins show as owned, including the 6 Deluxe-flagged bow/pistol/shotgun skins | Tested: pass (after the v1.0.0 fix that stopped skipping them) |
| Installs through Fluffy Mod Manager (listed in Fluffy's `installed.ini`) | Tested: pass |
| Loads alongside TLOU Infinite Ammo (both logs show active in the same launch) | Tested: pass (load only) |
| Equipping a Joel outfit / an Ellie outfit, seen in gameplay and cutscenes | Not tested |
| In-game (pause) menu Skins entry | Not tested |
| Skin stays after death/checkpoint and chapter load | Not tested |
| Points total unchanged, Gameplay Modifiers still locked | Not tested |
| Trophies not triggered by the unlocks | Not tested |
| Controller input through the `xinput1_4.dll` proxy | Not tested |
| `UnlockAllSkins=0`: game's locks return | Not tested |
| Removing the mod with an unlocked skin equipped: save loads, skin falls back | Not tested |
| Fluffy uninstall removes all three files | Not tested |
| tlou-i-l.exe in-game | Not tested |
| Epic Games Store version | Not tested |

## Notes

- During testing, an older hand-installed outfit mod ("Ellie Hospital Outfit")
  was removed from the test machine. That involved game data files
  (`build\pc\main\pak68.txt`, `bin\dc1\look2\characters.bin`) and is unrelated
  to this mod, which changes no files.
