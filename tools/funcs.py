"""Function start (after int3/padding) for RVAs, and direct callers of those starts. usage: funcs.py exe RVA..."""
import sys, os, re, struct
sys.path.insert(0, os.path.dirname(__file__)); import exe_refs as X
def start_of(rva):
    i = rva
    while i > X.t0 and not (X.img[i - 1] == 0xCC and X.img[i - 2] == 0xCC): i -= 1
    return i
def callers(fn):
    out = []
    for m in re.finditer(rb'\xE8', X.img[X.t0:X.t1]):
        i = X.t0 + m.start()
        if i + 5 + struct.unpack_from('<i', X.img, i + 1)[0] == fn: out.append(i)
    return out
for a in sys.argv[2:]:
    s = start_of(int(a, 16)); c = callers(s)
    print('%s in func %08X, %d callers: %s' % (a, s, len(c), ' '.join('%X' % x for x in c[:15])))
