"""List every instruction in .text that addresses `target` rip-relatively. usage: riprefs.py exe RVA [RVA...]"""
import sys, os, struct
import re
sys.path.insert(0, os.path.dirname(__file__)); import exe_refs as X
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
md = Cs(CS_ARCH_X86, CS_MODE_64)
# ModRM bytes with mod=00 rm=101 (rip+disp32)
MODRM = re.compile(b'[' + b''.join(re.escape(bytes([m])) for m in range(256) if m & 0xC7 == 5) + b']')
def refs(target):
    out = []
    for m in MODRM.finditer(X.img, X.t0, X.t1):
        dpos = m.start() + 1
        disp = struct.unpack_from('<i', X.img, dpos)[0]
        imm = target - (dpos + 4 + disp)  # bytes of immediate after the disp32
        if imm not in (0, 1, 2, 4): continue
        if True:
            for back in range(2, 6):  # disp32 is 2..5 bytes into the instruction
                s = dpos - back
                ins = next(md.disasm(X.img[s:s + 15], s), None)
                if ins and ins.size == back + 4 + imm and 'rip' in ins.op_str:
                    out.append((s, ins.mnemonic + ' ' + ins.op_str)); break
    return sorted(set(out))
for a in sys.argv[2:]:
    r = refs(int(a, 16))
    print('== RVA %s: %d refs' % (a, len(r)))
    for s, txt in r: print('   %08X  %s' % (s, txt))
