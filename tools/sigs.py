"""Check the mod's signatures against an exe: each must match exactly once. usage: sigs.py exe..."""
import sys, re, pefile
SIGS = {
    # registration of the debug "Unlock All Extras Content" bool: lea r8,[flag]; lea rdx,[name]
    'unlock-all-reg': ('45 33 C9 4C 8D 05 ?? ?? ?? ?? 48 8D 15 ?? ?? ?? ?? 49 8B CE E8', 3),
    'main-menu-skins': ('32 D2 EB 02 8A D3 80 3D ?? ?? ?? ?? 00 0F 85 ?? ?? ?? ?? 48 63 0D', 6),
    'game-menu-skins': ('40 84 FF 0F 85 ?? ?? ?? ?? 84 C0 0F 85 ?? ?? ?? ?? 38 05 ?? ?? ?? ?? 0F 85 ?? ?? ?? ?? 40 84 F6', 17),
    'skin-owned': ('39 9F CC 00 00 00 74 ?? 45 84 FF 75 ?? 40 84 F6 75', 0),
    'skin-equip': ('39 9A CC 00 00 00 74 ?? 48 63 8A D0 00 00 00', 0),
}
def rx(p): return re.compile(b''.join(b'.' if t == '??' else re.escape(bytes([int(t, 16)])) for t in p.split()), re.S)
for path in sys.argv[1:]:
    pe = pefile.PE(path, fast_load=True); img = pe.get_memory_mapped_image()
    t = next(s for s in pe.sections if s.Characteristics & 0x20000000)
    print(path.split('/')[-1])
    for k, (p, at) in SIGS.items():
        hits = [m.start() for m in rx(p).finditer(img, t.VirtualAddress, t.VirtualAddress + t.Misc_VirtualSize)]
        print('  %-16s %d hit(s) %s' % (k, len(hits), ' '.join('%X' % (h + at) for h in hits[:5])))
