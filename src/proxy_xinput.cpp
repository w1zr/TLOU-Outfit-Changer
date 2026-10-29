// xinput1_4.dll proxy. The game imports XINPUT1_4.dll, and Windows looks in the
// game folder before System32, so dropping this DLL there loads the mod with
// no third-party loader. It uses a different name from TLOU Infinite Ammo's
// version.dll so both mods can be installed together. Every export forwards
// to the real System32 DLL, including the ordinal-only ones.
#include <windows.h>

namespace {

HMODULE g_real = nullptr;
INIT_ONCE g_once = INIT_ONCE_STATIC_INIT;

BOOL CALLBACK LoadReal(PINIT_ONCE, PVOID, PVOID*) {
    wchar_t path[MAX_PATH];
    const UINT n = GetSystemDirectoryW(path, MAX_PATH);
    if (n == 0 || n > MAX_PATH - 16) return TRUE;
    lstrcatW(path, L"\\xinput1_4.dll");
    g_real = LoadLibraryW(path);
    return TRUE;
}

FARPROC Real(const char* name) {
    InitOnceExecuteOnce(&g_once, LoadReal, nullptr, nullptr);
    return g_real ? GetProcAddress(g_real, name) : nullptr;
}

template <typename Fn>
Fn Get(const char* name) {
    static_assert(sizeof(Fn) == sizeof(FARPROC));
    return reinterpret_cast<Fn>(Real(name));
}

} // namespace

// Called before the real DLL can be loaded (or if it is missing): report "no
// controller" rather than crash.
#define FWD(ret, fail, name, params, args)                                  \
    extern "C" ret WINAPI Proxy_##name params {                              \
        using Fn = ret(WINAPI*) params;                                      \
        static Fn fn = Get<Fn>(#name);                                       \
        if (!fn) return fail;                                                \
        return fn args;                                                      \
    }

// Undocumented ordinal-only exports; forwarded with pointer-sized args so
// nothing is truncated.
#define FWD_ORD(ord)                                                         \
    extern "C" ULONG_PTR WINAPI Proxy_Ord##ord(ULONG_PTR a, ULONG_PTR b, ULONG_PTR c, ULONG_PTR d) { \
        using Fn = ULONG_PTR(WINAPI*)(ULONG_PTR, ULONG_PTR, ULONG_PTR, ULONG_PTR); \
        static Fn fn = Get<Fn>(MAKEINTRESOURCEA(ord));                       \
        if (!fn) return ERROR_DEVICE_NOT_CONNECTED;                          \
        return fn(a, b, c, d);                                               \
    }

FWD(DWORD, ERROR_DEVICE_NOT_CONNECTED, XInputGetState, (DWORD a, LPVOID b), (a, b))
FWD(DWORD, ERROR_DEVICE_NOT_CONNECTED, XInputSetState, (DWORD a, LPVOID b), (a, b))
FWD(DWORD, ERROR_DEVICE_NOT_CONNECTED, XInputGetCapabilities, (DWORD a, DWORD b, LPVOID c), (a, b, c))
FWD(DWORD, ERROR_DEVICE_NOT_CONNECTED, XInputGetBatteryInformation, (DWORD a, BYTE b, LPVOID c), (a, b, c))
FWD(DWORD, ERROR_DEVICE_NOT_CONNECTED, XInputGetKeystroke, (DWORD a, DWORD b, LPVOID c), (a, b, c))
FWD(DWORD, ERROR_DEVICE_NOT_CONNECTED, XInputGetAudioDeviceIds, (DWORD a, LPWSTR b, UINT* c, LPWSTR d, UINT* e), (a, b, c, d, e))

extern "C" void WINAPI Proxy_XInputEnable(BOOL enable) {
    using Fn = void(WINAPI*)(BOOL);
    static Fn fn = Get<Fn>("XInputEnable");
    if (fn) fn(enable);
}

FWD_ORD(100) // XInputGetStateEx
FWD_ORD(101) // XInputWaitForGuideButton
FWD_ORD(102) // XInputCancelGuideButtonWait
FWD_ORD(103) // XInputPowerOffController
FWD_ORD(104) // XInputGetBaseBusInformation
FWD_ORD(108) // XInputGetCapabilitiesEx
FWD_ORD(109)
