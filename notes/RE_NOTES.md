# Reverse-engineering notes: skins in TLOU Part I

Target: `tlou-i.exe` 1.1.4.0, Steam build 18995818 (`.pdb` path says `t1xfinal-pc-1.1.5`).
RVAs below are for that build. Tools are in `tools/` (run with `python -E -P`).

## Data (bin/dc1)

DC format: `00CD`, u32 version, u32 data size, u32 string-table offset, then the
module header at 0x10 (u32 ?, u32 entry count, u64 entries offset). Entries are
24 bytes `{sid name, sid type, ptr}`. After `size`: u32 byte count, then a bitmap
with one bit per qword (set = the qword is a pointer/file offset). SIDs are FNV-1a 64.

- `sp-bonuses.bin` has 6 entries: `*sp-bonus-gameplay-modifiers*`, `*sp-bonus-weapons*`,
  `*sp-skins*`, `*podcast-doc-entries*`, `*sp-bonus-camera-filters*`, `*sp-bonus-concept-gallery*`.
- `*sp-skins*`: 2 categories (joel: 54, ellie: 318) of `sp-skin-entry`
  `{name, sid, skins-viewer-entry name, sid}`. It maps costume variants
  (backpack/goggles) to a skins-viewer entry. **There's no cost or unlock data here.**
- `skins-viewer.bin`: 74 `model-viewer-model` records. Relevant fields:
  `+0xB8` sid of the localized name (`MENU_SKIN_*`), `+0xCC` u32 point cost,
  `+0xD0` i32 bit index into the unlocked-skins bitset, `+0xE4` flags
  (bit 2 = preorder-bonus entitlement, bit 4 = deluxe-edition entitlement).
  Each record also has a `_locked.png` and an unlocked icon.

Conclusion: a data edit can't remove the Extras > Skins gate, so the release
uses the exe approach (Approach A).

## Code

| RVA | What |
|---|---|
| 0x5B8107B | Debug "Unlock All Extras Content" bool (`.data`). Registered at 0x12A145F, reset to 0 at 0x12A283C. 34 reads. |
| 0x1BF12BD | `IsMainMenuItemUnlocked(item)`: a switch on SID: `main-menu-concept-art`, `-gameplay-modifiers`, `-skins`, `-render-modes`, `-model-viewer`. Returns 1 = unlocked, 2 = locked. |
| 0x1BF13A2 | `main-menu-skins` case: unlocked if `unlockAll` (cmp at **0x1BF13FF**) OR `profile.game-completed[slot]` (`[profile + idx*4 + 0x4710]`) OR `deluxe-edition` entitlement OR byte 0x5EE4145. |
| 0x5B80FB0 | Bonus manager global. `+0x20` = 128-bit unlocked-skins bitset (`unlocked-skins` in the profile), `+0x70` = points spent. |
| 0x12A87E4 / 0x12A8770 | Buy skin: checks points `>= model+0xCC`, sets the bit `model+0xD0`, adds the cost to points spent, sends analytics `bonus-skinviewer-skins-unlocked`. |
| 0x12A6D3C | `IsSkinOwned(set, model)`: true if cost == 0, bit set ([rcx+0x48/0x50]), preorder entitlement or deluxe entitlement. **Does not read unlockAll.** Callers 0x12A6EED, 0x12A7CD1. |
| 0x12A7820 | Owned check for the *selected* skin (cost == 0 or bit in [mgr+0x20]). Called from 0x12A3DD3, probably the "selected skin not available" check (`Menu2::RootGame::OnSelectedSkinsButNotAvailable`). |
| 0x12A6C18 / 0x12A711C / 0x12A6EF4 | IsUnlocked for camera filters / gameplay modifiers / concept gallery. Each tests unlockAll first. **Leave these alone.** |

Strings: `"Unlock All Extras Content"` 0x2C90CC8, `"deluxe-edition"` 0x2C90E78,
`"preorder-bonus"` 0x2C90E28, `"unlocked-skins"` 0x2E07488, `"game-completed"` 0x2C97980.

## Patch plan (to confirm in-game)

1. Menu gate: redirect only the disp32 of the `cmp byte [unlockAll], 0` at 0x1BF13FF
   to a private byte set to 1. This affects only the `main-menu-skins` case.
   The other 33 reads, and therefore gameplay modifiers, filters and gallery,
   are untouched.
2. Owned skins (built): each `cmp dword [model+0xCC], ebx; je owned` in the two
   display checks (0x12A6E38, 0x12A77E1) and the equip check (0x12A784A) jumps
   to a stub that returns "owned" while the flag is on. That includes the six
   skins flagged Deluxe Edition (+0xE4 bit 4): in the base game they're bought
   with points after the story like every other skin (the buy routine
   0x12A87E4 never reads the flag; the lock text is "Complete game at any
   difficulty"), and Deluxe owners just get them free.
3. Nothing is written to the bitset, the points or the profile. The game itself
   saves `selected-*-skin` when you equip one. **Verify** what happens on load
   once the mod is removed.
