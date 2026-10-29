"""Find code references to SIDs (as imm64) and strings (rip-relative lea) in tlou-i.exe."""
import sys, os, re, struct, pefile
sys.path.insert(0, os.path.dirname(__file__)); import dc
pe = pefile.PE(sys.argv[1], fast_load=True)
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Characteristics & 0x20000000)
t0, t1 = text.VirtualAddress, text.VirtualAddress + text.Misc_VirtualSize
def sid_refs(name):
    b = struct.pack('<Q', dc.sid(name))
    return [m.start() for m in re.finditer(re.escape(b), img)]
def str_rvas(pat):
    return [(m.start(), m.group().decode()) for m in re.finditer(pat.encode(), img)]
def lea_refs(rva):
    out = []
    for m in re.finditer(rb'[\x48\x4C][\x8D\x8B][\x05\x0D\x15\x1D\x25\x2D\x35\x3D]', img[t0:t1]):
        i = t0 + m.start()
        if i + 7 + struct.unpack_from('<i', img, i + 3)[0] == rva: out.append(i)
    return out
if __name__ == '__main__':
    for n in sys.argv[2:]:
        r = sid_refs(n)
        print('%-40s sid %016X  refs %s' % (n, dc.sid(n), [hex(x) + ('(code)' if t0 <= x < t1 else '') for x in r][:12]))
