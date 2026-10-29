import sys, os, pickle, struct
sys.path.insert(0, os.path.dirname(__file__)); import dc
names = pickle.load(open(os.path.join(os.path.dirname(__file__), 'names.pkl'), 'rb'))
f = dc.DC(open(sys.argv[1], 'rb').read())
def show(o, n):
    for i in range(n):
        a = o + 8 * i; q = f.u64(a)
        tag = ''
        if f.is_ptr(a):
            tag = '-> 0x%X' % q
            if q >= f.strtab: tag += ' "%s"' % f.cstr(q)
            elif q >= 8: tag += ' [pre %s]' % names.get(f.u64(q - 8), '')
        elif q in names: tag = 'sid ' + names[q]
        else:
            lo, hi = struct.unpack('<ii', struct.pack('<Q', q)); fl = struct.unpack('<ff', struct.pack('<Q', q))
            tag = 'i32 %d %d  f %.3g %.3g' % (lo, hi, fl[0], fl[1])
        print('  %06X: %016X  %s' % (a, q, tag))
for spec in sys.argv[2:]:
    o, n = spec.split(':'); print('== 0x' + o); show(int(o, 16), int(n))
