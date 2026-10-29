#include "config.h"

#include <windows.h>

namespace {

bool ReadBool(const wchar_t* ini, const wchar_t* key, bool def) {
    return GetPrivateProfileIntW(L"OutfitChanger", key, def ? 1 : 0, ini) != 0;
}

} // namespace

Config LoadConfig(const wchar_t* ini) {
    Config c;
    c.unlockAllSkins = ReadBool(ini, L"UnlockAllSkins", c.unlockAllSkins);
    c.logging = ReadBool(ini, L"Logging", c.logging);
    return c;
}
