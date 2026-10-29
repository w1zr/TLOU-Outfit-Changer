// Game integration: identifies the host executable, finds the engine's skin
// checks in the loaded image and points them at a byte the mod owns.
#pragma once

namespace game {

// True when running inside tlou-i.exe or tlou-i-l.exe.
bool IsSupportedHost();

// Scans the main module and installs every patch, or none: on any mismatch
// it logs the reason, writes nothing and returns false.
bool Install();

} // namespace game
