#include "config.h"
#include "game.h"
#include "log.h"

#include <windows.h>

#define MOD_VERSION "1.0.0"

namespace {

// Builds "<game folder>\<file>" from the host executable's path.
bool GamePath(const wchar_t* file, wchar_t* out, DWORD cap) {
    const DWORD n = GetModuleFileNameW(nullptr, out, cap);
    if (n == 0 || n >= cap) return false;
    wchar_t* slash = wcsrchr(out, L'\\');
    if (!slash) return false;
    slash[1] = 0;
    return wcscat_s(out, cap, file) == 0;
}

// Scanning the image takes a moment, so it runs off the loader lock. It
// finishes long before the first menu is drawn.
DWORD WINAPI Worker(LPVOID) {
    game::Install();
    return 0;
}

void Init() {
    // xinput1_4.dll is loaded by other processes too (launchers, overlays).
    if (!game::IsSupportedHost()) return;

    wchar_t ini[MAX_PATH], log[MAX_PATH];
    if (!GamePath(L"TLOUOutfitChanger.ini", ini, MAX_PATH) || !GamePath(L"TLOUOutfitChanger.log", log, MAX_PATH)) return;

    const Config cfg = LoadConfig(ini);
    logx::Open(log, cfg.logging);
    logx::Write("TLOU Outfit Changer " MOD_VERSION " loaded");
    logx::Write("config: UnlockAllSkins=%d", cfg.unlockAllSkins);
    if (!cfg.unlockAllSkins) {
        logx::Write("UnlockAllSkins=0: nothing changed, the game's own locks apply");
        return;
    }
    HANDLE t = CreateThread(nullptr, 0, Worker, nullptr, 0, nullptr);
    if (t) CloseHandle(t);
    else logx::Write("ERROR: could not create worker thread (%lu)", GetLastError());
}

} // namespace

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(inst);
        Init();
    }
    return TRUE;
}
