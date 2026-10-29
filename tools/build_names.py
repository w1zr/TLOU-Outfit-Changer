import sys, os, pickle
sys.path.insert(0, os.path.dirname(__file__)); import dc
game, out = sys.argv[1], sys.argv[2]
blobs = [open(os.path.join(game, 'tlou-i.exe'), 'rb').read()]
d1 = os.path.join(game, 'bin', 'dc1')
for f in os.listdir(d1):
    if f.endswith('.bin'): blobs.append(open(os.path.join(d1, f), 'rb').read())
names = dc.names_from(blobs)
for f in os.listdir(d1):  # file names themselves, with *x* decoration used for module symbols
    b = f[:-4]
    for v in (b, '*' + b + '*'): names[dc.sid(v)] = v
for f in os.listdir(game):
    b = os.path.splitext(f)[0]; names[dc.sid(b)] = b
pickle.dump(names, open(out, 'wb'))
print(len(names))
