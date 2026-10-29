"""Disassemble around code that references given strings. usage: xref.py exe "string" | @RVA[:before:after] ..."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__)); import exe_refs as X
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.skipdata = True  # keep going past bytes that do not decode
import pickle
NAMES = pickle.load(open(os.path.join(os.path.dirname(__file__), 'names.pkl'), 'rb'))
def note(op):
    m = re.search(r'0x([0-9a-f]{9,16})', op)
    return '   ; ' + NAMES[int(m.group(1), 16)] if m and int(m.group(1), 16) in NAMES else ''
def dis(rva, before=0x30, after=0x60):
    for ins in md.disasm(X.img[rva - before: rva + after], rva - before):
        print('   %s%08X  %-8s %s%s' % ('>' if ins.address == rva else ' ', ins.address, ins.mnemonic, ins.op_str, note(ins.op_str)))
if __name__ == '__main__':
    for s in sys.argv[2:]:
        if s.startswith('@'):  # @RVA[:before:after] disassembles there
            a = [int(x, 16) for x in s[1:].split(':')]
            dis(*a); continue
        for rva, txt in X.str_rvas(re.escape(s) + r'\x00'):
            refs = X.lea_refs(rva)
            print('== "%s" @RVA %X  refs %s' % (txt[:-1], rva, [hex(r) for r in refs]))
            for r in refs[:3]: dis(r)
