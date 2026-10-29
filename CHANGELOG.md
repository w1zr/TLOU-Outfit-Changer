# Changelog

## v1.0.0 (2026-10-28)

First release.

- Opens Extras > Skins and the in-game Skins menu without finishing the story.
- Every skin is owned without spending points: all Joel and Ellie outfits and
  weapon skins, including the six bow, 9mm pistol and pump shotgun skins the
  Deluxe Edition gives early.
- Uses the game's own skin system; no game, save or profile files are changed.
- Loads as `xinput1_4.dll`, so it can be installed alongside TLOU Infinite Ammo
  (`version.dll`).
- Locates every patch site by signature with exact match counts and
  cross-checks. On any mismatch it logs the reason and changes nothing.
- Fluffy Mod Manager package: `modinfo.ini`, preview card, empty log so
  uninstall removes it too.
- `UnlockAllSkins=0` in the ini turns the mod off.
