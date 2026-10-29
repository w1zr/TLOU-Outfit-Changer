# TLOU Outfit Changer

<img src="art/logo.png" width="96" align="right" alt="">

Every Joel and Ellie outfit and weapon skin in **The Last of Us Part I** (PC),
without finishing the story.

- **Extras > Skins** in the main menu and the **Skins** entry in the in-game
  menu are open on any save, including a fresh profile.
- Every skin is already owned, so you spend no points: all 74 entries in the
  skins viewer, including the six bow, pistol and shotgun skins the Deluxe
  Edition gives early.
- It uses the game's own skin system and menus. No model or texture files are
  replaced.
- Points, Gameplay Modifiers and trophies are not changed. The mod never
  writes save or profile files.
- Works alongside [TLOU Infinite Ammo](https://github.com/w1zr/TLOU-Infinite-Ammo):
  this mod loads as `xinput1_4.dll`, Infinite Ammo as `version.dll`.

## Supported versions

| Game | Version | Status |
|---|---|---|
| Steam, `tlou-i.exe` | 1.1.4.0 (build 18995818) | Tested in-game |
| Steam, `tlou-i-l.exe` | 1.1.4.0 | Offline signature tests only |
| Epic Games Store | — | Not tested. The mod turns itself off safely if the executable doesn't match |

The mod finds the code it needs by byte pattern when the game starts. If a game
update changes that code, it writes the reason to `TLOUOutfitChanger.log` and
changes nothing.

## Install with Fluffy Mod Manager (recommended)

1. Close the game.
2. Copy `TLOUOutfitChanger-v1.0.0.zip` into `Fluffy Mod Manager\Games\TLOU\Mods\`.
3. Open Fluffy, choose The Last of Us Part I and tick **TLOU Outfit Changer**.
   Fluffy copies `xinput1_4.dll`, `TLOUOutfitChanger.ini` and
   `TLOUOutfitChanger.log` next to `tlou-i.exe` and records them.

## Install manually

Copy `xinput1_4.dll` and `TLOUOutfitChanger.ini` into the game folder (the
folder with `tlou-i.exe`), e.g.
`C:\Program Files (x86)\Steam\steamapps\common\The Last of Us Part I\`.
`modinfo.ini` and `screenshot.png` are only for Fluffy.

If you install by hand, don't also install the zip through Fluffy: Fluffy would
treat your copies as original game files and put them back on uninstall.

## Uninstall

- **Fluffy:** untick the mod. Fluffy deletes the three files it installed.
- **Manual:** delete `xinput1_4.dll`, `TLOUOutfitChanger.ini` and
  `TLOUOutfitChanger.log` from the game folder.

Skins you equipped are saved by the game itself. Removing the mod while one of
them is equipped has not been tested yet (see TEST_REPORT.md).

## Settings (`TLOUOutfitChanger.ini`)

| Key | Default | Meaning |
|---|---|---|
| `UnlockAllSkins` | 1 | Skins menus open and every skin owned. 0 = the game's own locks |
| `Logging` | 1 | Write `TLOUOutfitChanger.log` |

## Check it's working

`TLOUOutfitChanger.log` in the game folder should end with:

```
found: owned check RVA 0x12A6E38
found: owned check RVA 0x12A77E1
found: equip check RVA 0x12A784A
installed: Skins menus open, every skin owned
```

| Symptom | Cause / fix |
|---|---|
| No `TLOUOutfitChanger.log` | `xinput1_4.dll` isn't next to `tlou-i.exe` |
| Log says `Mod disabled; nothing was changed` | Game version not supported; the mod stayed off on purpose |
| Log ends with `UnlockAllSkins=0` | Turned off in the ini |

## Compatibility

- **TLOU Infinite Ammo:** tested together; both load.
- **Outfit or texture mods** (`.pak` files, `build\pc\main` loose files):
  this mod changes no game files. Mods that replace `characters.bin` or
  `pak68.txt` change what a skin looks like, not whether it's unlocked.
- **Other `xinput1_4.dll` mods:** can't be installed at the same time (same
  file name). Fluffy reports the conflict.
- **Online/Steam:** Part I is a single-player game. The mod only changes the
  running game in memory.

## How it works (for modders)

The game decides skin access in three places:

1. **Menu entry.** `IsMainMenuItemUnlocked()` switches on the item's name; the
   `main-menu-skins` case unlocks when the debug bool "Unlock All Extras
   Content" is set, or the profile's `game-completed`, or the Deluxe Edition
   entitlement. The in-game menu has the same check. The mod points only those
   two compares at a byte it owns (same-length disp32 rewrite). The debug bool
   has 34 readers, including Gameplay Modifiers, so it's never written.
2. **Owned or locked.** Two checks in the skins viewer and one in the equip
   path test `cost == 0` (`cmp dword [skin+0xCC], ebx; je owned`) among other
   conditions. Each 8-byte cmp/je is replaced with a jump to a small stub that
   returns "owned" while the mod is on, and otherwise runs the original
   instructions.
3. The bought-skins bitset, points and profile are never touched.

Every site is located by signature with exact match counts and cross-checks;
if anything doesn't match, nothing is written. Details: `notes/RE_NOTES.md`.

## Building from source

Requirements: Windows, Visual Studio 2022 Build Tools with "Desktop
development with C++". No other dependencies.

```bat
build.bat
build\scan_test.exe "C:\...\The Last of Us Part I\tlou-i.exe" "C:\...\tlou-i-l.exe"
package.bat
```

`build.bat` produces `build\xinput1_4.dll` (the mod) and `build\scan_test.exe`,
which checks every signature, the stubs and the failure paths against the real
game executables without running the game. `package.bat` builds
`release\TLOUOutfitChanger-v1.0.0.zip`.

Source layout: `src/dllmain.cpp` (startup), `src/proxy_xinput.cpp` +
`xinput.def` (loader shim; forwards all 14 XInput exports to System32),
`src/scan.*` (patterns and stub builders, no Windows dependencies),
`src/game.*` (patching), `src/config.*`, `src/log.*`. Python tools for the
game's data files are in `tools/` (`dc.py` for DC scripts, `psarc.py` for
`.psarc` archives).

## License

MIT. See `LICENSE`.
