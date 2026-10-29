// Offline test for the signature scanner. Maps a game executable from disk the
// same way Windows lays it out in memory and checks that every skin site
// resolves, that it matches the values verified by disassembly for known
// builds, that the stubs encode correctly, and that a damaged image is
// rejected instead of yielding a bogus address.
//
// usage: scan_test.exe <path to tlou-i.exe> [<path to tlou-i-l.exe> ...]
#include "../src/scan.h"

#include <windows.h>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <vector>

static int g_failures = 0;
#define CHECK(cond, ...)                                     \
    do {                                                     \
        if (cond) { std::printf("  PASS  "); }               \
        else { std::printf("  FAIL  "); ++g_failures; }      \
        std::printf(__VA_ARGS__);                            \
        std::printf("\n");                                   \
    } while (0)

struct Mapped {
    std::vector<uint8_t> image;
    scan::Range code;
    std::vector<scan::Range> data;
    uint32_t stamp = 0;
};

static bool MapImage(const char* path, Mapped& m) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return false;
    std::vector<uint8_t> file((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
    auto* dos = reinterpret_cast<IMAGE_DOS_HEADER*>(file.data());
    auto* nt = reinterpret_cast<IMAGE_NT_HEADERS64*>(file.data() + dos->e_lfanew);
    m.stamp = nt->FileHeader.TimeDateStamp;
    m.image.assign(nt->OptionalHeader.SizeOfImage, 0);
    std::memcpy(m.image.data(), file.data(), nt->OptionalHeader.SizeOfHeaders);
    auto* sec = IMAGE_FIRST_SECTION(nt);
    for (WORD i = 0; i < nt->FileHeader.NumberOfSections; ++i) {
        const size_t n = (std::min)(sec[i].SizeOfRawData, sec[i].Misc.VirtualSize);
        std::memcpy(m.image.data() + sec[i].VirtualAddress, file.data() + sec[i].PointerToRawData, n);
        const scan::Range r{sec[i].VirtualAddress, sec[i].VirtualAddress + sec[i].Misc.VirtualSize};
        const DWORD ch = sec[i].Characteristics;
        if (ch & IMAGE_SCN_MEM_EXECUTE) {
            if (!m.code.end) m.code = r;
        } else if ((ch & IMAGE_SCN_MEM_READ) && !(ch & IMAGE_SCN_MEM_DISCARDABLE)) {
            m.data.push_back(r);
        }
    }
    return true;
}

static void TestParser() {
    std::printf("parser\n");
    auto p = scan::Parse("32 C9 ?? 0d");
    CHECK(p.bytes.size() == 4 && p.bytes[0] == 0x32 && p.bytes[2] == -1 && p.bytes[3] == 0x0D, "parse hex and wildcards");
    const uint8_t buf[] = {0x00, 0x32, 0xC9, 0x55, 0x0D, 0x32, 0xC9, 0x00, 0x0D};
    auto hits = scan::FindAll(buf, 0, sizeof(buf), p);
    CHECK(hits.size() == 2 && hits[0] == 1 && hits[1] == 5, "FindAll finds both wildcard matches");
    CHECK(scan::FindAll(buf, 0, 3, p).empty(), "FindAll does not read past the range");
}

struct Known {
    uint32_t stamp;
    size_t unlockAll, mainMenu, gameMenu;
    size_t owned[3]; // in address order
};
// Verified by disassembly of Steam build 18995818 (file version 1.1.4.0).
static const Known kKnown[] = {
    {0x685BEBE1, 0x5B8107B, 0x1BF13FF, 0x1BF17D2, {0x12A6E38, 0x12A77E1, 0x12A784A}},
};

// Runs the stub's decision for one skin record the way the CPU would: returns
// the address execution continues at.
static uint64_t Simulate(const std::vector<uint8_t>& stub, uint32_t cost, uint8_t flag) {
    // 0: cmp [flag], 0 ; 7: je original ; 9: jmp owned
    uint64_t target;
    if (flag != 0) {
        std::memcpy(&target, stub.data() + 15, 8);
        return target;
    }
    // 23: original cmp [reg+CC], ebx(=0) ; 29: jne back ; 31: jmp owned ; 45: jmp back
    std::memcpy(&target, stub.data() + (cost == 0 ? 37 : 51), 8);
    return target;
}

static void TestImage(const char* path) {
    std::printf("image %s\n", path);
    Mapped m;
    if (!MapImage(path, m)) {
        CHECK(false, "could not read file");
        return;
    }
    const auto r = scan::LocateSkinSites(m.image.data(), m.code, m.data);
    CHECK(r.ok, "all skin sites located%s%s", r.ok ? "" : ": ", r.error.c_str());
    if (!r.ok) return;
    std::printf("        unlock flag RVA 0x%zX, menus RVA 0x%zX / 0x%zX, timestamp 0x%08X\n", r.unlockAll,
                r.mainMenu.instr, r.gameMenu.instr, m.stamp);
    for (const auto& o : r.owned) std::printf("        %s check RVA 0x%zX\n", o.equip ? "equip" : "owned", o.offset);

    for (const auto& k : kKnown) {
        if (k.stamp != m.stamp) continue;
        bool same = r.unlockAll == k.unlockAll && r.mainMenu.instr == k.mainMenu && r.gameMenu.instr == k.gameMenu;
        for (size_t i = 0; i < 3; ++i) same = same && r.owned[i].offset == k.owned[i];
        CHECK(same, "matches disassembly for this build");
    }
    CHECK(r.unlockAll >= m.code.end, "debug flag lies outside the code section");
    CHECK(m.image[r.mainMenu.instr] == 0x80 && m.image[r.mainMenu.instr + 1] == 0x3D && m.image[r.mainMenu.instr + 6] == 0,
          "main menu read is cmp byte ptr [rip+flag], 0");
    CHECK(m.image[r.gameMenu.instr] == 0x38 && m.image[r.gameMenu.instr + 1] == 0x05,
          "in-game menu read is cmp byte ptr [rip+flag], al");

    const uint64_t base = 0x140000000ull, stubAt = base - 0x20000, flag = base - 0x10000;
    bool stubsOk = true, decisionsOk = true;
    for (const auto& o : r.owned) {
        const uint64_t site = base + o.offset, owned = base + o.owned;
        const auto code = scan::BuildOwnedStub(stubAt, site, owned, flag, o);
        const auto jump = scan::BuildSiteJump(site, stubAt);
        int32_t d, j;
        std::memcpy(&d, code.data() + 2, 4);
        std::memcpy(&j, jump.data() + 1, 4);
        stubsOk = stubsOk && code.size() == 59 && jump.size() == 8 && code[0] == 0x80 && code[1] == 0x3D &&
                  stubAt + 7 + d == flag && site + 5 + j == stubAt &&
                  std::memcmp(code.data() + 23, m.image.data() + o.offset, 6) == 0 &&
                  m.image[o.owned] == 0xB3 && m.image[o.owned + 1] == 0x01;
        // Paid and free skin; mod on and off.
        decisionsOk = decisionsOk && Simulate(code, 10, 1) == owned && Simulate(code, 0, 1) == owned &&
                      Simulate(code, 10, 0) == site + 8 && Simulate(code, 0, 0) == owned;
    }
    CHECK(stubsOk, "stubs test the mod's byte, re-run the original cmp, jump back after the site");
    CHECK(decisionsOk, "decision table: every skin owned when on; the game's own result when off");

    // Damage a menu read so it no longer targets the flag: must be rejected.
    {
        auto copy = m;
        copy.image[r.gameMenu.dispOffset] ^= 0x10;
        const auto bad = scan::LocateSkinSites(copy.image.data(), copy.code, copy.data);
        CHECK(!bad.ok, "rejects image whose menu check reads another byte (%s)", bad.error.c_str());
    }
    // Remove one ownership check: must be rejected, not patched partially.
    {
        auto copy = m;
        copy.image[r.owned[0].offset] = 0xCC;
        const auto bad = scan::LocateSkinSites(copy.image.data(), copy.code, copy.data);
        CHECK(!bad.ok && bad.owned.empty(), "rejects image with a missing ownership check (%s)", bad.error.c_str());
    }
    // Remove the debug menu string: must fail cleanly.
    {
        auto copy = m;
        for (const auto& d : copy.data)
            for (size_t i = d.begin; i + 25 < d.end; ++i)
                if (std::memcmp(copy.image.data() + i, "Unlock All Extras Content", 26) == 0) copy.image[i] = 'X';
        const auto bad = scan::LocateSkinSites(copy.image.data(), copy.code, copy.data);
        CHECK(!bad.ok, "fails safely when the debug menu string is missing (%s)", bad.error.c_str());
    }
}

int main(int argc, char** argv) {
    TestParser();
    for (int i = 1; i < argc; ++i) TestImage(argv[i]);
    std::printf("\n%s (%d failure%s)\n", g_failures ? "FAILED" : "ALL PASSED", g_failures, g_failures == 1 ? "" : "s");
    return g_failures ? 1 : 0;
}
