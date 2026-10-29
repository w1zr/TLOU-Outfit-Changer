import sys, os, pickle
sys.path.insert(0, os.path.dirname(__file__)); import dc
names = pickle.load(open(os.path.join(os.path.dirname(__file__), 'names.pkl'), 'rb'))
def N(h): return names.get(h, '#%016X' % h)
f = dc.DC(open(sys.argv[1], 'rb').read())
print('size 0x%X strtab 0x%X ptrs %d entries %d' % (f.size, f.strtab, len(f.ptrs), len(f.entries)))
for name, typ, p in f.entries:
    print('ENTRY %-50s type %-30s @0x%X  (pre-type %s)' % (N(name), N(typ), p, N(f.u64(p - 8))))
